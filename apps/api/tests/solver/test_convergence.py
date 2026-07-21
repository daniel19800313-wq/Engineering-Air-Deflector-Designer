"""Milestone 6 isolated convergence-engine tests."""
import unittest

from app.solver.convergence import ConvergenceDecision, ConvergenceEngine
from app.solver.core import EngineeringValue
from app.solver.residuals import ResidualMeasurement, ResidualState


class ReviewedTestCriterion:
    criterion_id = "test-criterion-v1"
    def is_satisfied(self, measurement: ResidualMeasurement) -> bool:
        return measurement.value.value == 0.0


class ConvergenceEngineTests(unittest.TestCase):
    def test_unavailable_residual_fails(self) -> None:
        state = ResidualState(0, (ResidualMeasurement("mass", EngineeringValue.unavailable("not implemented"), "test"),))
        result = ConvergenceEngine().decide(state, {"mass": ReviewedTestCriterion()}, True)
        self.assertEqual(result.decision, ConvergenceDecision.FAILED)

    def test_no_hidden_criterion_is_allowed(self) -> None:
        state = ResidualState(0, (ResidualMeasurement("mass", EngineeringValue.unavailable("not implemented"), "test"),))
        self.assertEqual(ConvergenceEngine().decide(state, {}, True).decision, ConvergenceDecision.FAILED)


if __name__ == "__main__":
    unittest.main()
