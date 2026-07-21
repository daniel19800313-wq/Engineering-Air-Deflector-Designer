"""Control-volume topology contracts without physical calculations."""
from dataclasses import dataclass
from enum import StrEnum

from .geometry import GeometryModel


class NodeKind(StrEnum):
    """Supported V0.1 control-volume node categories."""
    INLET = "inlet"
    DEFLECTOR = "deflector"
    OUTLET = "outlet"


@dataclass(frozen=True, slots=True)
class ControlVolumeNode:
    """One auditable location in the sequential graph."""
    node_id: str
    kind: NodeKind
    geometry_reference: str
    sequence_index: int


@dataclass(frozen=True, slots=True)
class ControlVolumeGraph:
    """Immutable linear V0.1 topology consumed by the state engine."""
    nodes: tuple[ControlVolumeNode, ...]


class ControlVolumeBuilder:
    """Build an explicit topology using a supplied, reviewed outlet order."""

    def build(self, geometry: GeometryModel, outlet_order: tuple[str, ...]) -> ControlVolumeGraph:
        """Create a graph; never infer engineering order from row/column alone."""
        known = {cell.cell_id for cell in geometry.outlets}
        if len(outlet_order) != len(known) or set(outlet_order) != known:
            raise ValueError("outlet_order must contain every cell exactly once")
        nodes = [ControlVolumeNode("inlet", NodeKind.INLET, "inlet", 0)]
        if geometry.deflector:
            nodes.append(ControlVolumeNode("deflector", NodeKind.DEFLECTOR, geometry.deflector.deflector_id, len(nodes)))
        for cell_id in outlet_order:
            nodes.append(ControlVolumeNode(f"outlet:{cell_id}", NodeKind.OUTLET, cell_id, len(nodes)))
        return ControlVolumeGraph(tuple(nodes))

