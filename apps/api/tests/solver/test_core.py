"""Milestone 1 tests for immutable solver core contracts."""

import unittest

from app.solver.core import Availability, EngineeringValue, Provenance, RunInputSnapshot, SolverMode


class EngineeringValueTests(unittest.TestCase):
    def test_unavailable_value_never_contains_placeholder(self) -> None:
        quantity = EngineeringValue[float].unavailable("physics relationship unavailable", "Pa")
        self.assertEqual(quantity.availability, Availability.UNAVAILABLE)
        self.assertIsNone(quantity.value)
        self.assertIsNone(quantity.provenance)

    def test_available_value_requires_provenance(self) -> None:
        provenance = Provenance("solver_calculated", "run-1", "test", "approved-test")
        quantity = EngineeringValue.available(1.0, "dimensionless", provenance)
        self.assertEqual(quantity.value, 1.0)
        self.assertEqual(quantity.provenance, provenance)

    def test_missing_unavailable_reason_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EngineeringValue[float].unavailable("")


class RunInputSnapshotTests(unittest.TestCase):
    def test_snapshot_copies_and_freezes_mapping(self) -> None:
        geometry = {"plenum": {"dimensions": [1, 2, 3]}}
        snapshot = RunInputSnapshot(
            run_id="run-1",
            schema_version="v0.1",
            solver_name="conservation-skeleton",
            solver_version="v0.1",
            requested_mode=SolverMode.RELATIVE,
            geometry=geometry,
        )
        geometry["plenum"]["dimensions"][0] = 99
        self.assertEqual(snapshot.geometry["plenum"]["dimensions"][0], 1)  # type: ignore[index]
        with self.assertRaises(TypeError):
            snapshot.geometry["new"] = "forbidden"  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()
