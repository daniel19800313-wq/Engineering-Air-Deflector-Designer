"""Residual reporting framework with no built-in residual equations."""
from dataclasses import dataclass
from typing import Protocol, Sequence

from .core import EngineeringValue
from .state import SolverWorkspace


@dataclass(frozen=True, slots=True)
class ResidualMeasurement:
    """One named residual produced by an injected reviewed evaluator."""
    name: str
    value: EngineeringValue[float]
    evaluator_id: str


@dataclass(frozen=True, slots=True)
class ResidualState:
    """Immutable residual report for one candidate iteration."""
    iteration_index: int
    measurements: tuple[ResidualMeasurement, ...]


class ResidualEvaluator(Protocol):
    """Extension interface for a reviewed residual definition."""
    @property
    def evaluator_id(self) -> str:
        """Return a stable versioned residual evaluator identity."""
        ...

    def evaluate(self, previous: SolverWorkspace, candidate: SolverWorkspace) -> ResidualMeasurement:
        """Evaluate one residual without mutating either workspace."""
        ...


class ResidualEngine:
    """Execute explicit evaluators and validate their report structure."""

    def evaluate(self, iteration_index: int, previous: SolverWorkspace, candidate: SolverWorkspace, evaluators: Sequence[ResidualEvaluator]) -> ResidualState:
        """Return residuals; an empty evaluator set is invalid, not converged."""
        if not evaluators:
            raise ValueError("at least one reviewed residual evaluator is required")
        results = tuple(evaluator.evaluate(previous, candidate) for evaluator in evaluators)
        names = [result.name for result in results]
        if len(names) != len(set(names)):
            raise ValueError("residual names must be unique")
        return ResidualState(iteration_index, results)

