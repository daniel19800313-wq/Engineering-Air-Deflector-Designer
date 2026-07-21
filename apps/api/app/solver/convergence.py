"""Convergence decision framework with no built-in tolerances."""
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping, Protocol

from .residuals import ResidualMeasurement, ResidualState


class ConvergenceDecision(StrEnum):
    """Possible decisions after residual evaluation."""
    CONTINUE = "continue"
    CONVERGED = "converged"
    FAILED = "failed"


class ResidualCriterion(Protocol):
    """Reviewed, versioned acceptance criterion for one residual."""
    @property
    def criterion_id(self) -> str:
        """Return stable provenance identity."""
        ...

    def is_satisfied(self, measurement: ResidualMeasurement) -> bool:
        """Decide one available residual using an external reviewed policy."""
        ...


@dataclass(frozen=True, slots=True)
class ConvergenceResult:
    """Auditable convergence decision for one iteration."""
    decision: ConvergenceDecision
    reason: str
    criterion_ids: tuple[str, ...]


class ConvergenceEngine:
    """Combine explicit residual criteria without hidden thresholds."""

    def decide(self, residuals: ResidualState, criteria: Mapping[str, ResidualCriterion], continuation_allowed: bool) -> ConvergenceResult:
        """Fail unavailable/unconfigured residuals; converge only when all pass."""
        if not residuals.measurements:
            return ConvergenceResult(ConvergenceDecision.FAILED, "no residuals were evaluated", ())
        criterion_ids: list[str] = []
        for measurement in residuals.measurements:
            criterion = criteria.get(measurement.name)
            if criterion is None:
                return ConvergenceResult(ConvergenceDecision.FAILED, f"criterion unavailable for {measurement.name}", tuple(criterion_ids))
            criterion_ids.append(criterion.criterion_id)
            if measurement.value.value is None:
                return ConvergenceResult(ConvergenceDecision.FAILED, f"residual unavailable: {measurement.name}", tuple(criterion_ids))
            if not criterion.is_satisfied(measurement):
                decision = ConvergenceDecision.CONTINUE if continuation_allowed else ConvergenceDecision.FAILED
                return ConvergenceResult(decision, f"criterion not satisfied: {measurement.name}", tuple(criterion_ids))
        return ConvergenceResult(ConvergenceDecision.CONVERGED, "all reviewed criteria satisfied", tuple(criterion_ids))

