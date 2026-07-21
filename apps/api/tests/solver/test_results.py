"""Milestone 7 isolated result-package tests."""
import unittest

from app.solver.results import ConfidenceLevel, ResultPackager, SolverProvenance
from app.solver.state import ExecutionState


class ResultPackagerTests(unittest.TestCase):
    def test_skeleton_never_exposes_absolute_placeholder(self) -> None:
        package = ResultPackager().package_conceptual(
            ExecutionState.FAILED,
            SolverProvenance("skeleton", "v0.1", "run-1", "hvac-review-approved", "execution-v0.1"),
            (), None, (),
        )
        self.assertEqual(package.confidence_level, ConfidenceLevel.CONCEPTUAL)
        self.assertIsNone(package.absolute_total_flow.value)
        self.assertFalse(package.recommendation_eligible)

    def test_nonterminal_state_cannot_be_packaged(self) -> None:
        with self.assertRaises(ValueError):
            ResultPackager().package_conceptual(
                ExecutionState.ITERATING,
                SolverProvenance("skeleton", "v0.1", "run-1", "review", "architecture"),
                (), None, (),
            )


if __name__ == "__main__":
    unittest.main()
