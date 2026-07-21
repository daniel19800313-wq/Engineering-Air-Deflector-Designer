"""Milestone 8 end-to-end executable-skeleton tests."""
import unittest

from app.solver.control_volume import ControlVolumeBuilder
from app.solver.core import RunInputSnapshot, SolverMode
from app.solver.framework import ExecutionPolicy, SolverFramework
from app.solver.results import ResultPackager, SolverProvenance
from app.solver.state import ExecutionState
from app.solver.visualization import VisualizationAdapter
from tests.solver.test_geometry import valid_geometry
from tests.solver.test_residuals import UnavailableResidual
from tests.solver.test_state import NoPhysicsDeflector, NoPhysicsOutlet, unavailable_segment


class NeverUsedCriterion:
    criterion_id = "test-never-used"
    def is_satisfied(self, measurement):
        raise AssertionError("unavailable residual must fail before criterion evaluation")


class FrameworkTests(unittest.TestCase):
    def test_executable_skeleton_fails_safely_with_unavailable_physics(self) -> None:
        geometry = valid_geometry()
        snapshot = RunInputSnapshot("run-1", "v0.1", "conservation-skeleton", "v0.1", SolverMode.RELATIVE, {"geometry_id": "test"})
        package = SolverFramework().execute(
            snapshot, geometry, tuple(cell.cell_id for cell in geometry.outlets), unavailable_segment("inlet"),
            NoPhysicsDeflector(), NoPhysicsOutlet(), (UnavailableResidual(),), {"mass": NeverUsedCriterion()}, ExecutionPolicy(1),
        )
        self.assertEqual(package.status, ExecutionState.FAILED)
        self.assertIsNone(package.outlets[0].extracted_flow.value)
        self.assertFalse(package.recommendation_eligible)

    def test_visualization_preserves_engineering_value_identity(self) -> None:
        outlet = NoPhysicsOutlet().evaluate(unavailable_segment("inlet"), "R0C0")
        package = ResultPackager().package_conceptual(ExecutionState.CONVERGED, SolverProvenance("s", "v", "r", "p", "a"), (outlet,), None, ())
        payload = VisualizationAdapter().create_payload(package)
        self.assertIs(payload.cells[0].extracted_flow, package.outlets[0].extracted_flow)

    def test_failed_iteration_never_reaches_visualization_cells(self) -> None:
        outlet = NoPhysicsOutlet().evaluate(unavailable_segment("inlet"), "R0C0")
        package = ResultPackager().package_conceptual(ExecutionState.FAILED, SolverProvenance("s", "v", "r", "p", "a"), (outlet,), None, ())
        self.assertEqual(VisualizationAdapter().create_payload(package).cells, ())


if __name__ == "__main__":
    unittest.main()
