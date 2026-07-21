"""Milestone 5 isolated residual-engine tests."""
import unittest

from app.solver.core import EngineeringValue
from app.solver.residuals import ResidualEngine, ResidualMeasurement
from app.solver.state import SolverWorkspace


class UnavailableResidual:
    evaluator_id = "test-unavailable-v1"
    def evaluate(self, previous: SolverWorkspace, candidate: SolverWorkspace) -> ResidualMeasurement:
        return ResidualMeasurement("mass", EngineeringValue.unavailable("physics residual not integrated", "dimensionless"), self.evaluator_id)


class ResidualEngineTests(unittest.TestCase):
    def test_requires_explicit_evaluator(self) -> None:
        with self.assertRaises(ValueError):
            ResidualEngine().evaluate(0, SolverWorkspace(), SolverWorkspace(), ())

    def test_preserves_unavailable_residual(self) -> None:
        state = ResidualEngine().evaluate(0, SolverWorkspace(), SolverWorkspace(), (UnavailableResidual(),))
        self.assertIsNone(state.measurements[0].value.value)


if __name__ == "__main__":
    unittest.main()
