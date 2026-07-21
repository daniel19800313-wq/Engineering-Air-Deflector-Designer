"""Validated geometry contracts; contains no airflow calculations."""

from dataclasses import dataclass
from math import isfinite

from .core import Diagnostic, DiagnosticSeverity


@dataclass(frozen=True, slots=True)
class Vector3:
    """Finite canonical-SI vector or point."""
    x: float
    y: float
    z: float


@dataclass(frozen=True, slots=True)
class BoxGeometry:
    """Rectangular plenum dimensions in metres."""
    width_m: float
    height_m: float
    depth_m: float


@dataclass(frozen=True, slots=True)
class InletGeometry:
    """Rectangular inlet geometry and supplied inward direction."""
    center_m: Vector3
    width_m: float
    height_m: float
    direction: Vector3


@dataclass(frozen=True, slots=True)
class OutletCellGeometry:
    """One outlet cell with explicit identity and canonical position."""
    cell_id: str
    row_index: int
    column_index: int
    center_m: Vector3
    clear_width_m: float
    clear_height_m: float
    normal: Vector3


@dataclass(frozen=True, slots=True)
class DeflectorGeometry:
    """Planar rectangular internal guide-plate geometry."""
    deflector_id: str
    center_m: Vector3
    insertion_length_m: float
    width_m: float
    thickness_m: float
    normal: Vector3


@dataclass(frozen=True, slots=True)
class GeometryModel:
    """Immutable V0.1 geometry accepted by downstream solver stages."""
    plenum: BoxGeometry
    inlet: InletGeometry
    outlets: tuple[OutletCellGeometry, ...]
    deflector: DeflectorGeometry | None


@dataclass(frozen=True, slots=True)
class GeometryValidationReport:
    """Geometry validation outcome and stable diagnostics."""
    is_valid: bool
    diagnostics: tuple[Diagnostic, ...]


class GeometryValidator:
    """Validate structural V0.1 geometry without repairing user input."""

    def validate(self, model: GeometryModel) -> GeometryValidationReport:
        """Return blocking diagnostics for invalid structural geometry."""
        issues: list[Diagnostic] = []
        dimensions = [model.plenum.width_m, model.plenum.height_m, model.plenum.depth_m]
        if any(not isfinite(value) or value <= 0 for value in dimensions):
            issues.append(self._error("GEOMETRY_PLENUM_DIMENSION", "Plenum dimensions must be positive."))
        if len(model.outlets) != 8:
            issues.append(self._error("GEOMETRY_OUTLET_COUNT", "V0.1 requires exactly eight outlet cells."))
        ids = [cell.cell_id for cell in model.outlets]
        if len(ids) != len(set(ids)):
            issues.append(self._error("GEOMETRY_DUPLICATE_CELL", "Outlet cell identifiers must be unique."))
        for cell in model.outlets:
            if not all(isfinite(value) and value > 0 for value in (cell.clear_width_m, cell.clear_height_m)):
                issues.append(self._error("GEOMETRY_CELL_AREA", "Outlet cell dimensions must be positive.", cell.cell_id))
        if model.deflector and (
            not isfinite(model.deflector.insertion_length_m) or model.deflector.insertion_length_m <= 0
            or not isfinite(model.deflector.width_m) or model.deflector.width_m <= 0
            or not isfinite(model.deflector.thickness_m) or model.deflector.thickness_m <= 0
        ):
            issues.append(self._error("GEOMETRY_DEFLECTOR_DIMENSION", "Deflector dimensions must be positive.", model.deflector.deflector_id))
        return GeometryValidationReport(not issues, tuple(issues))

    @staticmethod
    def _error(code: str, message: str, object_reference: str | None = None) -> Diagnostic:
        return Diagnostic(code, DiagnosticSeverity.BLOCKING_INPUT, "geometry_validation", message, object_reference=object_reference)
