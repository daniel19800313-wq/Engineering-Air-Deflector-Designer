"""Milestone 3 isolated control-volume tests."""
import unittest

from app.solver.control_volume import ControlVolumeBuilder, NodeKind
from tests.solver.test_geometry import valid_geometry


class ControlVolumeBuilderTests(unittest.TestCase):
    def test_preserves_explicit_reviewed_order(self) -> None:
        order = tuple(reversed([cell.cell_id for cell in valid_geometry().outlets]))
        graph = ControlVolumeBuilder().build(valid_geometry(), order)
        self.assertEqual(graph.nodes[0].kind, NodeKind.INLET)
        self.assertEqual(tuple(node.geometry_reference for node in graph.nodes[1:]), order)

    def test_rejects_incomplete_order(self) -> None:
        with self.assertRaises(ValueError):
            ControlVolumeBuilder().build(valid_geometry(), ("R0C0",))


if __name__ == "__main__":
    unittest.main()
