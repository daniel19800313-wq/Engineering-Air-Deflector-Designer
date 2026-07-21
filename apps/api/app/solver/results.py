"""Immutable solver result contracts and provenance-safe packaging."""
from dataclasses import dataclass
from enum import StrEnum

from .core import Diagnostic, EngineeringValue
from .residuals import ResidualState
from .state import ExecutionState, OutletState


class ClaimLevel(StrEnum):
    """Permitted engineering claim basis for a result."""
    NONE = "none"
    RELATIVE_ESTIMATE = "relative_estimate"
    VALIDATED_ABSOLUTE = "validated_absolute"


class ConfidenceLevel(StrEnum):
    """Categorical evidence level; never a numeric confidence score."""
    CONCEPTUAL = "conceptual"
    RELATIVE = "relative"
    CALIBRATED = "calibrated"
    VALIDATED = "validated"
    ENGINEERING_USE = "engineering_use"
    CERTIFIED_RESERVED = "certified_reserved"


@dataclass(frozen=True, slots=True)
class SolverProvenance:
    """Version identities governing one packaged run."""
    solver_name: str
    solver_version: str
    input_run_id: str
    physics_baseline: str
    execution_architecture: str


@dataclass(frozen=True, slots=True)
class ResultPackage:
    """Immutable terminal solver output consumed by persistence and UI."""
    status: ExecutionState
    claim_level: ClaimLevel
    confidence_level: ConfidenceLevel
    provenance: SolverProvenance
    outlets: tuple[OutletState, ...]
    residuals: ResidualState | None
    absolute_total_flow: EngineeringValue[float]
    diagnostics: tuple[Diagnostic, ...]
    recommendation_eligible: bool


class ResultPackager:
    """Package terminal state while enforcing unavailable/eligibility rules."""

    def package_conceptual(
        self,
        status: ExecutionState,
        provenance: SolverProvenance,
        outlets: tuple[OutletState, ...],
        residuals: ResidualState | None,
        diagnostics: tuple[Diagnostic, ...],
    ) -> ResultPackage:
        """Package the Sprint 1.5 skeleton without engineering claims."""
        if status not in {ExecutionState.CONVERGED, ExecutionState.FAILED, ExecutionState.ABORTED}:
            raise ValueError("result can be packaged only from a terminal solver state")
        return ResultPackage(
            status=status,
            claim_level=ClaimLevel.NONE,
            confidence_level=ConfidenceLevel.CONCEPTUAL,
            provenance=provenance,
            outlets=outlets,
            residuals=residuals,
            absolute_total_flow=EngineeringValue.unavailable(
                "absolute physics and validation are not integrated", "m3/s"
            ),
            diagnostics=diagnostics,
            recommendation_eligible=False,
        )
