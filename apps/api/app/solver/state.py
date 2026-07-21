"""Solver lifecycle and sequential-state engine; no physics models included."""
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from .control_volume import ControlVolumeGraph, NodeKind
from .core import EngineeringValue


class ExecutionState(StrEnum):
    """Governed solver lifecycle states."""
    IDLE = "idle"
    GEOMETRY_LOADED = "geometry_loaded"
    VALIDATED = "validated"
    INITIALIZED = "initialized"
    ITERATING = "iterating"
    CONVERGED = "converged"
    FAILED = "failed"
    ABORTED = "aborted"
    PACKAGED = "packaged"


_TRANSITIONS = {
    ExecutionState.IDLE: {ExecutionState.GEOMETRY_LOADED, ExecutionState.ABORTED},
    ExecutionState.GEOMETRY_LOADED: {ExecutionState.VALIDATED, ExecutionState.FAILED, ExecutionState.ABORTED},
    ExecutionState.VALIDATED: {ExecutionState.INITIALIZED, ExecutionState.FAILED, ExecutionState.ABORTED},
    ExecutionState.INITIALIZED: {ExecutionState.ITERATING, ExecutionState.FAILED, ExecutionState.ABORTED},
    ExecutionState.ITERATING: {ExecutionState.ITERATING, ExecutionState.CONVERGED, ExecutionState.FAILED, ExecutionState.ABORTED},
    ExecutionState.CONVERGED: {ExecutionState.PACKAGED},
    ExecutionState.FAILED: {ExecutionState.PACKAGED},
    ExecutionState.ABORTED: {ExecutionState.PACKAGED},
    ExecutionState.PACKAGED: set(),
}


@dataclass(slots=True)
class SolverStatus:
    """Mutable lifecycle status changed only through validated transitions."""
    state: ExecutionState = ExecutionState.IDLE
    terminal_reason: str | None = None

    def transition(self, target: ExecutionState, reason: str | None = None) -> None:
        """Apply one architecture-approved state transition."""
        if target not in _TRANSITIONS[self.state]:
            raise ValueError(f"invalid solver transition: {self.state} -> {target}")
        self.state = target
        self.terminal_reason = reason


@dataclass(frozen=True, slots=True)
class SegmentState:
    """Engineering state arriving at or leaving one graph node."""
    node_id: str
    remaining_flow: EngineeringValue[float]
    pressure: EngineeringValue[float]
    momentum_direction: EngineeringValue[tuple[float, float, float]]


@dataclass(frozen=True, slots=True)
class OutletState:
    """Auditable before/extracted/after state for one outlet."""
    outlet_id: str
    incoming: SegmentState
    extracted_flow: EngineeringValue[float]
    outgoing: SegmentState


class DeflectorInteraction(Protocol):
    """Future physics capability for one deflector interaction."""
    def evaluate(self, incoming: SegmentState, geometry_reference: str) -> SegmentState:
        """Return downstream state or explicit unavailable quantities."""
        ...


class OutletExtraction(Protocol):
    """Future physics capability for sequential outlet extraction."""
    def evaluate(self, incoming: SegmentState, outlet_reference: str) -> OutletState:
        """Return auditable extraction state or unavailable quantities."""
        ...


@dataclass(slots=True)
class SolverWorkspace:
    """Solver-private mutable workspace for accepted and candidate traces."""
    accepted_segments: list[SegmentState] = field(default_factory=list)
    accepted_outlets: list[OutletState] = field(default_factory=list)


class SequentialStateEngine:
    """Execute one topology pass using injected reviewed physics capabilities."""

    def execute_iteration(
        self,
        graph: ControlVolumeGraph,
        initial: SegmentState,
        deflector_model: DeflectorInteraction,
        outlet_model: OutletExtraction,
    ) -> SolverWorkspace:
        """Run nodes in graph order; no component can bypass state propagation."""
        workspace = SolverWorkspace()
        current = initial
        workspace.accepted_segments.append(current)
        for node in graph.nodes[1:]:
            if node.kind is NodeKind.DEFLECTOR:
                current = deflector_model.evaluate(current, node.geometry_reference)
                workspace.accepted_segments.append(current)
            elif node.kind is NodeKind.OUTLET:
                outlet = outlet_model.evaluate(current, node.geometry_reference)
                if outlet.incoming != current:
                    raise ValueError("outlet model must consume the current downstream state")
                workspace.accepted_outlets.append(outlet)
                current = outlet.outgoing
                workspace.accepted_segments.append(current)
        return workspace

