"""Milestone 4 isolated state-engine tests."""
import unittest

from app.solver.control_volume import ControlVolumeBuilder
from app.solver.core import EngineeringValue
from app.solver.state import ExecutionState, OutletState, SegmentState, SequentialStateEngine, SolverStatus
from tests.solver.test_geometry import valid_geometry


def unavailable_segment(node: str) -> SegmentState:
    return SegmentState(node, EngineeringValue.unavailable("physics not integrated", "relative"), EngineeringValue.unavailable("pressure model unavailable", "Pa"), EngineeringValue.unavailable("momentum model unavailable", "unit vector"))


class NoPhysicsDeflector:
    def evaluate(self, incoming: SegmentState, geometry_reference: str) -> SegmentState:
        return unavailable_segment(geometry_reference)


class NoPhysicsOutlet:
    def evaluate(self, incoming: SegmentState, outlet_reference: str) -> OutletState:
        return OutletState(outlet_reference, incoming, EngineeringValue.unavailable("outlet physics not integrated", "relative"), unavailable_segment(outlet_reference))


class StateEngineTests(unittest.TestCase):
    def test_state_machine_rejects_skipped_stage(self) -> None:
        with self.assertRaises(ValueError):
            SolverStatus().transition(ExecutionState.ITERATING)

    def test_iteration_propagates_each_outlet_outgoing_state(self) -> None:
        geometry = valid_geometry()
        order = tuple(cell.cell_id for cell in geometry.outlets)
        graph = ControlVolumeBuilder().build(geometry, order)
        result = SequentialStateEngine().execute_iteration(graph, unavailable_segment("inlet"), NoPhysicsDeflector(), NoPhysicsOutlet())
        self.assertEqual(len(result.accepted_outlets), 8)
        self.assertEqual(result.accepted_outlets[1].incoming.node_id, order[0])
        self.assertIsNone(result.accepted_outlets[-1].extracted_flow.value)


if __name__ == "__main__":
    unittest.main()
