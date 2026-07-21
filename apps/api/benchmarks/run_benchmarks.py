"""Standard-library timing harness for solver-framework operations only."""
from __future__ import annotations

import json
import os
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.solver.control_volume import ControlVolumeBuilder
from app.solver.core import EngineeringValue
from app.solver.geometry import BoxGeometry, GeometryModel, GeometryValidator, InletGeometry, OutletCellGeometry, Vector3
from app.solver.results import ResultPackager, SolverProvenance
from app.solver.state import ExecutionState, OutletState, SegmentState, SequentialStateEngine
from app.solver.visualization import VisualizationAdapter
from app.verification.interaction_runner import canonical_interaction_cases, result_payload
from app.solver.geometry_interaction import GeometryInteractionEvaluator
from app.solver.sequential_extraction import ConservationEvaluator, SequentialExtractionEvaluator
from app.verification.extraction_runner import POLICY as EXTRACTION_POLICY, canonical_extraction_cases, result_payload as extraction_payload
from app.solver.airflow_solver import DirectionalAreaDistanceKernel, ExperimentalAirflowSolver, ProjectedAreaReflectionInfluence
from app.verification.airflow_runner import POLICY as AIRFLOW_POLICY, base_input as airflow_input


def geometry() -> GeometryModel:
    """Return deterministic structural geometry without engineering expectations."""
    cells = tuple(OutletCellGeometry(f"R{i // 4}C{i % 4}", i // 4, i % 4, Vector3(i % 4, i // 4, 0), 0.1, 0.1, Vector3(0, 0, -1)) for i in range(8))
    return GeometryModel(BoxGeometry(1, 1, 1), InletGeometry(Vector3(0, 0, 1), 0.2, 0.2, Vector3(1, 0, 0)), cells, None)


def segment(node: str) -> SegmentState:
    """Return a state whose engineering quantities are explicitly unavailable."""
    return SegmentState(node, EngineeringValue.unavailable("benchmark has no physics"), EngineeringValue.unavailable("benchmark has no physics"), EngineeringValue.unavailable("benchmark has no physics"))


class Deflector:
    def evaluate(self, incoming, geometry_reference):
        return segment(geometry_reference)


class Outlet:
    def evaluate(self, incoming, outlet_reference):
        return OutletState(outlet_reference, incoming, EngineeringValue.unavailable("benchmark has no physics"), segment(outlet_reference))


def timed(name, operation):
    start = time.perf_counter_ns()
    value = operation()
    return value, {"operation": name, "elapsed_ns": time.perf_counter_ns() - start}


def main() -> int:
    """Measure framework stages and print JSON; no threshold is evaluated."""
    model = geometry()
    records = []
    _, record = timed("geometry_validation", lambda: GeometryValidator().validate(model)); records.append(record)
    graph, record = timed("control_volume_graph", lambda: ControlVolumeBuilder().build(model, tuple(cell.cell_id for cell in model.outlets))); records.append(record)
    initial, record = timed("state_initialization", lambda: segment("inlet")); records.append(record)
    workspace, record = timed("one_skeleton_iteration", lambda: SequentialStateEngine().execute_iteration(graph, initial, Deflector(), Outlet())); records.append(record)
    package, record = timed("result_packaging", lambda: ResultPackager().package_conceptual(ExecutionState.FAILED, SolverProvenance("benchmark", "v0.1", "benchmark-run", "approved-baseline", "execution-v0.1"), tuple(workspace.accepted_outlets), None, ())); records.append(record)
    _, record = timed("visualization_projection", lambda: VisualizationAdapter().create_payload(package)); records.append(record)
    interaction_case = canonical_interaction_cases()[1]
    interaction, record = timed("path_deflector_intersection", lambda: GeometryInteractionEvaluator().evaluate(interaction_case.path, interaction_case.plate, interaction_case.routing, interaction_case.policy)); records.append(record)
    _, record = timed("surface_classification_access", lambda: interaction.surface_relationship); records.append(record)
    _, record = timed("routing_classification_access", lambda: (interaction.routing, interaction.selected_downstream_cv_id)); records.append(record)
    _, record = timed("interaction_provenance_packaging", lambda: result_payload(interaction_case)["provenance"]); records.append(record)
    extraction_case = canonical_extraction_cases()[1]
    _, record = timed("extraction_instruction_validation", lambda: SequentialExtractionEvaluator().evaluate(canonical_extraction_cases()[0].inputs, EXTRACTION_POLICY)); records.append(record)
    one_result, record = timed("one_outlet_extraction_step", lambda: SequentialExtractionEvaluator().evaluate(canonical_extraction_cases()[0].inputs, EXTRACTION_POLICY)); records.append(record)
    sequence_result, record = timed("sequential_multi_outlet_execution", lambda: SequentialExtractionEvaluator().evaluate(extraction_case.inputs, EXTRACTION_POLICY)); records.append(record)
    _, record = timed("local_residual_packaging", lambda: one_result.accepted[0].residual); records.append(record)
    _, record = timed("global_conservation_packaging", lambda: sequence_result.global_residual); records.append(record)
    _, record = timed("extraction_provenance_packaging", lambda: extraction_payload(extraction_case)["accepted"][0]["source_reference"]); records.append(record)
    _, record = timed("experimental_airflow_solver_v0_1", lambda: ExperimentalAirflowSolver(DirectionalAreaDistanceKernel(),ProjectedAreaReflectionInfluence()).solve(airflow_input(),AIRFLOW_POLICY)); records.append(record)
    print(json.dumps({"kind": "framework_timing_only", "environment": {"python": platform.python_version(), "implementation": platform.python_implementation(), "platform": platform.platform(), "processor": platform.processor(), "logical_cpu_count": os.cpu_count()}, "measurements": records}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
