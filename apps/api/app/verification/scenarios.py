"""Physics-free execution scenarios for canonical framework cases."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from app.solver.control_volume import ControlVolumeBuilder
from app.solver.convergence import ConvergenceEngine
from app.solver.core import EngineeringValue, RunInputSnapshot, SolverMode
from app.solver.framework import ExecutionPolicy, SolverFramework
from app.solver.geometry import BoxGeometry, GeometryModel, InletGeometry, OutletCellGeometry, Vector3
from app.solver.residuals import ResidualMeasurement, ResidualState
from app.solver.results import ResultPackager, SolverProvenance
from app.solver.state import ExecutionState, OutletState, SegmentState, SequentialStateEngine, SolverWorkspace
from app.solver.visualization import VisualizationAdapter

from .schema import VerificationCase


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    """Deterministic contract result, deliberately excluding engineering values."""
    payload: Mapping[str, object]
    unsupported: bool = False


def _geometry(case: VerificationCase) -> GeometryModel:
    count = int(case.geometry_input.get("outlet_count", 8))
    width = float(case.geometry_input.get("plenum_width_m", 1.0))
    outlets = tuple(OutletCellGeometry(f"R{index // 4}C{index % 4}", index // 4, index % 4, Vector3(index % 4, index // 4, 0), 0.1, 0.1, Vector3(0, 0, -1)) for index in range(count))
    return GeometryModel(BoxGeometry(width, 1, 1), InletGeometry(Vector3(0, 0, 1), 0.2, 0.2, Vector3(1, 0, 0)), outlets, None)


def _segment(node: str) -> SegmentState:
    return SegmentState(node, EngineeringValue.unavailable("physics not integrated", "relative"), EngineeringValue.unavailable("pressure unavailable", "Pa"), EngineeringValue.unavailable("momentum unavailable", "unit vector"))


class _NoPhysicsDeflector:
    def evaluate(self, incoming: SegmentState, geometry_reference: str) -> SegmentState:
        return _segment(geometry_reference)


class _Outlet:
    def __init__(self, reject_at: str | None = None) -> None:
        self.reject_at = reject_at
    def evaluate(self, incoming: SegmentState, outlet_reference: str) -> OutletState:
        consumed = _segment("wrong") if outlet_reference == self.reject_at else incoming
        return OutletState(outlet_reference, consumed, EngineeringValue.unavailable("outlet physics not integrated", "relative"), _segment(outlet_reference))


class _UnavailableResidual:
    evaluator_id = "unavailable-residual-v1"
    def evaluate(self, previous: SolverWorkspace, candidate: SolverWorkspace) -> ResidualMeasurement:
        return ResidualMeasurement("mass", EngineeringValue.unavailable("residual physics unavailable", "dimensionless"), self.evaluator_id)


def _package_payload(package) -> dict[str, object]:
    return {
        "status": package.status.value,
        "diagnostics": sorted(item.code for item in package.diagnostics),
        "claim_level": package.claim_level.value,
        "confidence_level": package.confidence_level.value,
        "available_quantities": [],
        "unavailable_quantities": ["absolute_total_flow"],
        "provenance": {
            "solver_name": package.provenance.solver_name,
            "solver_version": package.provenance.solver_version,
            "input_run_id": package.provenance.input_run_id,
        },
        "recommendation_eligible": package.recommendation_eligible,
    }


def execute_case(case: VerificationCase) -> ScenarioResult:
    """Execute one named framework scenario without airflow expectations."""
    scenario = str(case.evaluator_configuration.get("scenario", "unavailable_physics"))
    geometry = _geometry(case)
    order = case.control_volume_order
    if scenario == "missing_order":
        try:
            ControlVolumeBuilder().build(geometry, ())
        except ValueError:
            return ScenarioResult({"status": "specification_failure", "diagnostics": ["MISSING_EXPLICIT_OUTLET_ORDER"], "claim_level": "none", "confidence_level": "conceptual", "available_quantities": [], "unavailable_quantities": [], "provenance": {}, "recommendation_eligible": False})
    if scenario == "missing_criteria":
        residual = ResidualState(0, (ResidualMeasurement("mass", EngineeringValue.unavailable("not integrated"), "test"),))
        result = ConvergenceEngine().decide(residual, {}, True)
        return ScenarioResult({"status": result.decision.value, "diagnostics": ["MISSING_CONVERGENCE_CRITERIA"], "claim_level": "none", "confidence_level": "conceptual", "available_quantities": [], "unavailable_quantities": ["mass_residual"], "provenance": {}, "recommendation_eligible": False})
    if scenario in {"candidate_rejection", "failed_partial_isolation"}:
        graph = ControlVolumeBuilder().build(geometry, order or ())
        try:
            SequentialStateEngine().execute_iteration(graph, _segment("inlet"), _NoPhysicsDeflector(), _Outlet(reject_at=(order or ("",))[0]))
        except ValueError:
            return ScenarioResult({"status": "failed", "diagnostics": ["CANDIDATE_STATE_REJECTED"], "claim_level": "none", "confidence_level": "conceptual", "available_quantities": [], "unavailable_quantities": ["candidate_state"], "provenance": {}, "recommendation_eligible": False})
    if scenario == "accepted_state_commit":
        graph = ControlVolumeBuilder().build(geometry, order or ())
        workspace = SequentialStateEngine().execute_iteration(graph, _segment("inlet"), _NoPhysicsDeflector(), _Outlet())
        return ScenarioResult({"status": "accepted", "diagnostics": [], "claim_level": "none", "confidence_level": "conceptual", "available_quantities": [], "unavailable_quantities": ["outlet_physics"], "provenance": {"accepted_outlet_count": len(workspace.accepted_outlets)}, "recommendation_eligible": False})
    if scenario == "visualization_identity":
        outlet = _Outlet().evaluate(_segment("inlet"), "R0C0")
        package = ResultPackager().package_conceptual(ExecutionState.CONVERGED, SolverProvenance("skeleton", "v0.1", case.case_id, "approved", "v0.1"), (outlet,), None, ())
        payload = VisualizationAdapter().create_payload(package)
        preserved = payload.cells[0].extracted_flow is package.outlets[0].extracted_flow
        result = _package_payload(package)
        result["provenance"] = {"value_identity_preserved": preserved}
        return ScenarioResult(result)
    snapshot = RunInputSnapshot(case.case_id, "v0.1", "conservation-skeleton", "v0.1", SolverMode.RELATIVE, case.geometry_input)
    package = SolverFramework().execute(snapshot, geometry, order or (), _segment("inlet"), _NoPhysicsDeflector(), _Outlet(), (_UnavailableResidual(),), {}, ExecutionPolicy(1))
    payload = _package_payload(package)
    if scenario == "forced_non_converged":
        payload["diagnostics"] = sorted(set(payload["diagnostics"]) | {"NOT_CONVERGED"})
    return ScenarioResult(payload)
