"""Governed sequential transported-quantity conservation evaluator.

Extraction amounts are explicit inputs.  This module predicts no HVAC behavior.
"""
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from .core import Availability, DiagnosticSeverity, EngineeringValue, Provenance
from .state import OutletState, SegmentState


class ExtractionSource(StrEnum):
    """Governed origins permitted for extraction instructions."""
    MEASURED = "measured"
    PRESCRIBED_TEST_INPUT = "prescribed_test_input"
    EXTERNALLY_EVALUATED = "externally_evaluated"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ExtractionProvenance:
    """Traceable source and evaluator identity for extraction accounting."""
    source: ExtractionSource
    source_reference: str
    evaluator_version: str


@dataclass(frozen=True, slots=True)
class ExtractionDiagnostic:
    """Stable extraction validation or conservation diagnostic."""
    code: str
    severity: DiagnosticSeverity
    message: str
    outlet_id: str | None = None


@dataclass(frozen=True, slots=True)
class ExtractionPolicy:
    """Explicit unit and residual comparison policy with provenance."""
    unit: str
    comparison_tolerance: float
    tolerance_provenance: Provenance
    evaluator_version: str

    def __post_init__(self) -> None:
        if not self.unit or not self.evaluator_version:
            raise ValueError("unit and evaluator_version are required")
        if not isfinite(self.comparison_tolerance) or self.comparison_tolerance < 0:
            raise ValueError("comparison_tolerance must be explicit, finite, and non-negative")


@dataclass(frozen=True, slots=True)
class OutletExtractionInstruction:
    """Explicit extraction quantity for exactly one declared outlet."""
    outlet_id: str
    extracted: EngineeringValue[float]
    provenance: ExtractionProvenance | None


@dataclass(frozen=True, slots=True)
class ExtractionInput:
    """Immutable inlet quantity, outlet order, and instructions for one sequence."""
    inlet: EngineeringValue[float]
    outlet_order: tuple[str, ...]
    declared_outlet_ids: tuple[str, ...]
    instructions: tuple[OutletExtractionInstruction, ...]


@dataclass(frozen=True, slots=True)
class ConservationResidual:
    """Explicit conservation residual and comparison outcome."""
    residual: EngineeringValue[float]
    conserved: bool | None
    policy_provenance: Provenance


@dataclass(frozen=True, slots=True)
class ControlVolumeExtractionResult:
    """Accepted local incoming/extracted/downstream accounting record."""
    outlet_id: str
    incoming: EngineeringValue[float]
    extracted: EngineeringValue[float]
    downstream: EngineeringValue[float]
    residual: ConservationResidual
    provenance: ExtractionProvenance


@dataclass(frozen=True, slots=True)
class SequentialExtractionResult:
    """Immutable completed sequence or explicit failed partial result."""
    completed: bool
    inlet: EngineeringValue[float]
    accepted: tuple[ControlVolumeExtractionResult, ...]
    total_extracted: EngineeringValue[float]
    terminal_downstream: EngineeringValue[float]
    global_residual: ConservationResidual
    diagnostics: tuple[ExtractionDiagnostic, ...]
    recommendation: None = None


class ConservationEvaluator:
    """Evaluate an already specified local conservation candidate."""

    def evaluate(self, incoming: EngineeringValue[float], extracted: EngineeringValue[float], downstream: EngineeringValue[float], policy: ExtractionPolicy) -> ConservationResidual:
        """Return explicit residual; unavailable operands never imply conservation."""
        operands = (incoming, extracted, downstream)
        if any(item.availability is Availability.UNAVAILABLE for item in operands):
            return ConservationResidual(EngineeringValue.unavailable("conservation operand unavailable", policy.unit), None, policy.tolerance_provenance)
        if any(item.unit != policy.unit for item in operands):
            return ConservationResidual(EngineeringValue.unavailable("conservation unit mismatch", policy.unit), None, policy.tolerance_provenance)
        residual_value = incoming.value - extracted.value - downstream.value  # type: ignore[operator]
        provenance = Provenance("solver_calculated", policy.evaluator_version, "conservation_evaluator", "authorized_conservation_accounting")
        residual = EngineeringValue.available(residual_value, policy.unit, provenance)
        return ConservationResidual(residual, abs(residual_value) <= policy.comparison_tolerance, policy.tolerance_provenance)


class SequentialExtractionEvaluator:
    """Validate and execute explicit extraction instructions in declared order."""

    def evaluate(self, inputs: ExtractionInput, policy: ExtractionPolicy) -> SequentialExtractionResult:
        """Accept each local candidate only after validation and conservation."""
        diagnostic = self._validate_structure(inputs, policy)
        if diagnostic:
            return self._failed(inputs, policy, (), diagnostic)
        if inputs.inlet.availability is Availability.UNAVAILABLE:
            return self._failed(inputs, policy, (), ExtractionDiagnostic("SE_INLET_UNAVAILABLE", DiagnosticSeverity.BLOCKING_INPUT, "Inlet transported quantity is unavailable."))
        if inputs.inlet.unit != policy.unit or not self._valid_available(inputs.inlet):
            return self._failed(inputs, policy, (), ExtractionDiagnostic("SE_INVALID_INLET", DiagnosticSeverity.BLOCKING_INPUT, "Inlet quantity is invalid or uses an incompatible unit."))
        by_outlet = {item.outlet_id: item for item in inputs.instructions}
        accepted: list[ControlVolumeExtractionResult] = []
        current = inputs.inlet
        total = 0.0
        for outlet_id in inputs.outlet_order:
            instruction = by_outlet[outlet_id]
            diagnostic = self._validate_instruction(instruction, current, policy)
            if diagnostic:
                return self._failed(inputs, policy, tuple(accepted), diagnostic)
            extracted_value = instruction.extracted.value
            downstream_value = current.value - extracted_value  # type: ignore[operator]
            calculated_provenance = Provenance("solver_calculated", policy.evaluator_version, "sequential_extraction", f"remaining_after:{outlet_id}")
            downstream = EngineeringValue.available(downstream_value, policy.unit, calculated_provenance)
            residual = ConservationEvaluator().evaluate(current, instruction.extracted, downstream, policy)
            if residual.conserved is not True:
                return self._failed(inputs, policy, tuple(accepted), ExtractionDiagnostic("SE_LOCAL_CONSERVATION_FAILED", DiagnosticSeverity.NUMERICAL_FAILURE, "Local conservation comparison failed.", outlet_id))
            candidate = ControlVolumeExtractionResult(outlet_id, current, instruction.extracted, downstream, residual, instruction.provenance)  # type: ignore[arg-type]
            accepted.append(candidate)
            current = downstream
            total += extracted_value  # type: ignore[operator]
        total_value = EngineeringValue.available(total, policy.unit, Provenance("solver_calculated", policy.evaluator_version, "sequential_extraction", "total_extracted"))
        global_residual = ConservationEvaluator().evaluate(inputs.inlet, total_value, current, policy)
        if global_residual.conserved is not True:
            return self._failed(inputs, policy, tuple(accepted), ExtractionDiagnostic("SE_GLOBAL_CONSERVATION_FAILED", DiagnosticSeverity.NUMERICAL_FAILURE, "Global conservation comparison failed."), total_value, current, global_residual)
        return SequentialExtractionResult(True, inputs.inlet, tuple(accepted), total_value, current, global_residual, ())

    def _validate_structure(self, inputs, policy):
        if not inputs.outlet_order or len(set(inputs.outlet_order)) != len(inputs.outlet_order):
            return ExtractionDiagnostic("SE_INVALID_ORDER", DiagnosticSeverity.BLOCKING_INPUT, "Outlet order must be explicit and unique.")
        if tuple(inputs.outlet_order) != tuple(inputs.declared_outlet_ids):
            return ExtractionDiagnostic("SE_ORDER_MISMATCH", DiagnosticSeverity.BLOCKING_INPUT, "Outlet order must match declared control-volume order.")
        ids = [item.outlet_id for item in inputs.instructions]
        if len(ids) != len(set(ids)):
            return ExtractionDiagnostic("SE_DUPLICATE_INSTRUCTION", DiagnosticSeverity.BLOCKING_INPUT, "Duplicate outlet instruction.")
        if set(ids) != set(inputs.declared_outlet_ids):
            return ExtractionDiagnostic("SE_UNDECLARED_OR_MISSING_OUTLET", DiagnosticSeverity.BLOCKING_INPUT, "Instructions must reference every declared outlet exactly once.")
        return None

    def _validate_instruction(self, instruction, incoming, policy):
        value = instruction.extracted
        if instruction.provenance is None or not instruction.provenance.source_reference or not instruction.provenance.evaluator_version:
            return ExtractionDiagnostic("SE_PROVENANCE_MISSING", DiagnosticSeverity.BLOCKING_INPUT, "Extraction provenance is required.", instruction.outlet_id)
        if instruction.provenance.source is ExtractionSource.UNAVAILABLE or value.availability is Availability.UNAVAILABLE:
            return ExtractionDiagnostic("SE_EXTRACTION_UNAVAILABLE", DiagnosticSeverity.BLOCKING_INPUT, "Extraction quantity is unavailable.", instruction.outlet_id)
        if value.provenance is None:
            return ExtractionDiagnostic("SE_VALUE_PROVENANCE_MISSING", DiagnosticSeverity.BLOCKING_INPUT, "Available extraction value requires value provenance.", instruction.outlet_id)
        if value.unit != policy.unit:
            return ExtractionDiagnostic("SE_UNIT_MISMATCH", DiagnosticSeverity.BLOCKING_INPUT, "Extraction unit is incompatible.", instruction.outlet_id)
        if not self._valid_available(value) or value.value < 0:  # type: ignore[operator]
            return ExtractionDiagnostic("SE_INVALID_EXTRACTION", DiagnosticSeverity.BLOCKING_INPUT, "Extraction must be finite and non-negative.", instruction.outlet_id)
        if value.value > incoming.value:  # type: ignore[operator]
            return ExtractionDiagnostic("SE_EXTRACTION_EXCEEDS_INCOMING", DiagnosticSeverity.BLOCKING_INPUT, "Extraction exceeds available incoming quantity.", instruction.outlet_id)
        return None

    @staticmethod
    def _valid_available(value):
        return value.availability is Availability.AVAILABLE and value.value is not None and isfinite(value.value)

    def _failed(self, inputs, policy, accepted, diagnostic, total=None, terminal=None, residual=None):
        unavailable = EngineeringValue.unavailable("sequence did not complete", policy.unit)
        global_residual = residual or ConservationResidual(unavailable, None, policy.tolerance_provenance)
        return SequentialExtractionResult(False, inputs.inlet, accepted, total or unavailable, terminal or unavailable, global_residual, (diagnostic,))


class ExtractionStateAdapter:
    """Adapt one governed instruction to the existing OutletExtraction interface."""

    def __init__(self, instruction: OutletExtractionInstruction, policy: ExtractionPolicy):
        self.instruction = instruction
        self.policy = policy
        self.last_result: ControlVolumeExtractionResult | None = None

    def evaluate(self, incoming: SegmentState, outlet_reference: str) -> OutletState:
        """Return candidate outlet state without mutating accepted incoming state."""
        inputs = ExtractionInput(incoming.remaining_flow, (outlet_reference,), (outlet_reference,), (self.instruction,))
        result = SequentialExtractionEvaluator().evaluate(inputs, self.policy)
        if not result.completed:
            raise ValueError(result.diagnostics[0].code)
        local = result.accepted[0]
        self.last_result = local
        outgoing = SegmentState(outlet_reference, local.downstream, incoming.pressure, incoming.momentum_direction)
        return OutletState(outlet_reference, incoming, local.extracted, outgoing)
