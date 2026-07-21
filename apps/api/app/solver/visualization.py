"""Read-only visualization interface over packaged solver results."""
from dataclasses import dataclass

from .core import EngineeringValue
from .results import ClaimLevel, ConfidenceLevel, ResultPackage
from .state import ExecutionState


@dataclass(frozen=True, slots=True)
class VisualizationCell:
    """One solver-provided outlet value exposed without derivation."""
    outlet_id: str
    extracted_flow: EngineeringValue[float]


@dataclass(frozen=True, slots=True)
class VisualizationPayload:
    """Read-only UI payload containing no client-derived engineering quantity."""
    status: ExecutionState
    claim_level: ClaimLevel
    confidence_level: ConfidenceLevel
    cells: tuple[VisualizationCell, ...]
    recommendation_eligible: bool


class VisualizationAdapter:
    """Select solver output fields for visualization without calculating them."""

    def create_payload(self, package: ResultPackage) -> VisualizationPayload:
        """Return engineering values by identity from the immutable result package."""
        cells = () if package.status is not ExecutionState.CONVERGED else tuple(
            VisualizationCell(item.outlet_id, item.extracted_flow) for item in package.outlets
        )
        return VisualizationPayload(
            package.status,
            package.claim_level,
            package.confidence_level,
            cells,
            package.recommendation_eligible,
        )
