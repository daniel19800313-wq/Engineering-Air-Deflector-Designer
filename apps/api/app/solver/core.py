"""Core immutable contracts shared by all solver milestones."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Generic, Mapping, TypeVar


T = TypeVar("T")


def _freeze(value: object) -> object:
    """Recursively freeze JSON-like run input without inventing values."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


class SolverMode(StrEnum):
    """Engineering claim mode explicitly requested for a run."""

    RELATIVE = "relative"
    ABSOLUTE = "absolute"


class Availability(StrEnum):
    """Whether an engineering quantity is available from the solver."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class DiagnosticSeverity(StrEnum):
    """Stable severity categories used by solver diagnostics."""

    INFO = "info"
    WARNING = "warning"
    BLOCKING_INPUT = "blocking_input"
    NUMERICAL_FAILURE = "numerical_failure"
    OUTSIDE_ENVELOPE = "outside_envelope"
    INTERNAL_FAILURE = "internal_failure"
    ABORTED = "aborted"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Traceable origin of one supplied or calculated quantity."""

    source_type: str
    source_reference: str
    solver_component: str | None = None
    model_relationship: str | None = None


@dataclass(frozen=True, slots=True)
class EngineeringValue(Generic[T]):
    """Engineering value that is either available with provenance or unavailable.

    Construction helpers enforce that missing quantities never become zero or a
    guessed default.
    """

    availability: Availability
    value: T | None
    unit: str | None
    provenance: Provenance | None
    unavailable_reason: str | None

    @classmethod
    def available(cls, value: T, unit: str, provenance: Provenance) -> EngineeringValue[T]:
        """Create an available value with unit and provenance."""
        if value is None:
            raise ValueError("available engineering value cannot be None")
        if not unit:
            raise ValueError("available engineering value requires a unit")
        return cls(Availability.AVAILABLE, value, unit, provenance, None)

    @classmethod
    def unavailable(cls, reason: str, unit: str | None = None) -> EngineeringValue[T]:
        """Create an explicitly unavailable value without fabricating data."""
        if not reason:
            raise ValueError("unavailable engineering value requires a reason")
        return cls(Availability.UNAVAILABLE, None, unit, None, reason)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Stable solver event suitable for audit and user-safe presentation."""

    code: str
    severity: DiagnosticSeverity
    stage: str
    user_message: str
    engineering_detail: str | None = None
    object_reference: str | None = None


@dataclass(frozen=True, slots=True)
class RunInputSnapshot:
    """Immutable top-level input accepted by the solver framework."""

    run_id: str
    schema_version: str
    solver_name: str
    solver_version: str
    requested_mode: SolverMode
    geometry: Mapping[str, object]
    boundary_conditions: Mapping[str, object] = field(default_factory=dict)
    fluid_state: Mapping[str, object] = field(default_factory=dict)
    calibration_reference: str | None = None

    def __post_init__(self) -> None:
        """Freeze input mappings so a run cannot observe caller mutations."""
        for name in ("run_id", "schema_version", "solver_name", "solver_version"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        object.__setattr__(self, "geometry", _freeze(self.geometry))
        object.__setattr__(self, "boundary_conditions", _freeze(self.boundary_conditions))
        object.__setattr__(self, "fluid_state", _freeze(self.fluid_state))
