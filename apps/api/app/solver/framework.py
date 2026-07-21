"""Top-level executable orchestration of the physics-free solver framework."""
from dataclasses import dataclass
from typing import Mapping, Sequence

from .control_volume import ControlVolumeBuilder
from .convergence import ConvergenceDecision, ConvergenceEngine, ResidualCriterion
from .core import Diagnostic, DiagnosticSeverity, RunInputSnapshot
from .geometry import GeometryModel, GeometryValidator
from .residuals import ResidualEngine, ResidualEvaluator, ResidualState
from .results import ResultPackage, ResultPackager, SolverProvenance
from .state import DeflectorInteraction, ExecutionState, OutletExtraction, SegmentState, SequentialStateEngine, SolverStatus, SolverWorkspace


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    """Explicit iteration policy; intentionally has no hidden default."""
    maximum_iterations: int

    def __post_init__(self) -> None:
        if self.maximum_iterations <= 0:
            raise ValueError("maximum_iterations must be explicitly positive")


class SolverFramework:
    """Execute approved lifecycle stages using injected future-physics capabilities."""

    def execute(
        self,
        snapshot: RunInputSnapshot,
        geometry: GeometryModel,
        outlet_order: tuple[str, ...],
        initial_state: SegmentState,
        deflector_model: DeflectorInteraction,
        outlet_model: OutletExtraction,
        residual_evaluators: Sequence[ResidualEvaluator],
        convergence_criteria: Mapping[str, ResidualCriterion],
        policy: ExecutionPolicy,
    ) -> ResultPackage:
        """Run the skeleton; all physics and numerical policies are explicit inputs."""
        status = SolverStatus()
        diagnostics: list[Diagnostic] = []
        residual_state: ResidualState | None = None
        workspace = SolverWorkspace()
        try:
            status.transition(ExecutionState.GEOMETRY_LOADED)
            validation = GeometryValidator().validate(geometry)
            diagnostics.extend(validation.diagnostics)
            if not validation.is_valid:
                status.transition(ExecutionState.FAILED, "geometry validation failed")
            else:
                status.transition(ExecutionState.VALIDATED)
                graph = ControlVolumeBuilder().build(geometry, outlet_order)
                status.transition(ExecutionState.INITIALIZED)
                status.transition(ExecutionState.ITERATING)
                previous = SolverWorkspace()
                for iteration_index in range(policy.maximum_iterations):
                    workspace = SequentialStateEngine().execute_iteration(graph, initial_state, deflector_model, outlet_model)
                    residual_state = ResidualEngine().evaluate(iteration_index, previous, workspace, residual_evaluators)
                    decision = ConvergenceEngine().decide(
                        residual_state,
                        convergence_criteria,
                        continuation_allowed=iteration_index + 1 < policy.maximum_iterations,
                    )
                    if decision.decision is ConvergenceDecision.CONVERGED:
                        status.transition(ExecutionState.CONVERGED, decision.reason)
                        break
                    if decision.decision is ConvergenceDecision.FAILED:
                        status.transition(ExecutionState.FAILED, decision.reason)
                        break
                    previous = workspace
                    status.transition(ExecutionState.ITERATING, decision.reason)
                if status.state is ExecutionState.ITERATING:
                    status.transition(ExecutionState.FAILED, "iteration policy exhausted")
        except (ValueError, TypeError) as exc:
            if status.state not in {ExecutionState.FAILED, ExecutionState.ABORTED}:
                status.transition(ExecutionState.FAILED, str(exc))
            diagnostics.append(Diagnostic("FRAMEWORK_EXECUTION_FAILED", DiagnosticSeverity.INTERNAL_FAILURE, "execution", "The solver framework could not complete the run.", str(exc)))

        return ResultPackager().package_conceptual(
            status.state,
            SolverProvenance(snapshot.solver_name, snapshot.solver_version, snapshot.run_id, "HVAC_DOMAIN_REVIEW_PACKAGE-approved", "ADD-V0.1-execution"),
            tuple(workspace.accepted_outlets), residual_state, tuple(diagnostics),
        )

