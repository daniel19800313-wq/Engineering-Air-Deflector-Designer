"""Governed geometric path/deflector interaction evaluator.

This module evaluates geometry and declared routing only.  It creates no flow,
pressure, resistance, extraction, loss, or performance quantity.
"""
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite, sqrt

from .core import Diagnostic, DiagnosticSeverity, Provenance
from .geometry import Vector3
from .state import SegmentState


class InteractionClassification(StrEnum):
    """Deterministic V0.1 path/plate geometric classifications."""
    NO_INTERSECTION = "no_intersection"
    FACE_INTERSECTION = "face_intersection"
    EDGE_INTERSECTION = "edge_intersection"
    CORNER_INTERSECTION = "corner_intersection"
    COPLANAR_OR_AMBIGUOUS = "coplanar_or_ambiguous"
    BLOCKED_BY_GEOMETRY = "blocked_by_geometry"
    UNSUPPORTED_GEOMETRY = "unsupported_geometry"
    INVALID_INPUT = "invalid_input"


class SurfaceRelationship(StrEnum):
    """Geometric incident orientation relative to the plate normal."""
    FRONT_FACING = "front_facing"
    BACK_FACING = "back_facing"
    EDGE = "edge"
    CORNER = "corner"
    AMBIGUOUS = "ambiguous"
    NONE = "none"


class RoutingClassification(StrEnum):
    """Routing outcomes limited to caller-declared control-volume references."""
    CONTINUE_DECLARED_PATH = "continue_declared_path"
    REDIRECT_TO_DECLARED_DOWNSTREAM_CV = "redirect_to_declared_downstream_cv"
    TERMINATE_DUE_TO_BLOCKAGE = "terminate_due_to_blockage"
    UNAVAILABLE = "unavailable"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class IncomingGeometricPath:
    """Finite path with explicit origin, direction, and geometric extent."""
    path_id: str
    origin: Vector3
    direction: Vector3
    extent_m: float


@dataclass(frozen=True, slots=True)
class PlanarDeflectorReference:
    """Explicit rectangular plate frame; axes and dimensions are caller supplied."""
    deflector_id: str
    surface_id: str
    center: Vector3
    normal: Vector3
    width_axis: Vector3
    insertion_axis: Vector3
    width_m: float
    insertion_length_m: float
    geometry_kind: str = "planar_rectangle"


@dataclass(frozen=True, slots=True)
class DeclaredRouting:
    """Only downstream relationships the evaluator is allowed to select."""
    valid_downstream_cv_ids: tuple[str, ...]
    continue_cv_id: str | None
    redirected_cv_id: str | None
    blocked: bool


@dataclass(frozen=True, slots=True)
class GeometryInteractionPolicy:
    """Explicit computational geometry policy with no hidden tolerance."""
    geometric_tolerance_m: float
    direction_tolerance: float
    evaluator_version: str


@dataclass(frozen=True, slots=True)
class InteractionProvenance:
    """Audit trail for one interaction and routing decision."""
    path_id: str
    deflector_id: str
    surface_id: str
    operation_id: str
    classification_rule_id: str
    selected_relationship: str | None
    evaluator_version: str


@dataclass(frozen=True, slots=True)
class GeometryInteractionResult:
    """Immutable geometric result or explicit unavailable/rejected outcome."""
    interaction: InteractionClassification
    routing: RoutingClassification
    intersection_point: Vector3 | None
    surface_id: str | None
    surface_normal: Vector3 | None
    surface_relationship: SurfaceRelationship
    selected_downstream_cv_id: str | None
    provenance: InteractionProvenance
    diagnostics: tuple[Diagnostic, ...]
    available: bool


def _dot(a: Vector3, b: Vector3) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


def _sub(a: Vector3, b: Vector3) -> Vector3:
    return Vector3(a.x - b.x, a.y - b.y, a.z - b.z)


def _add_scaled(a: Vector3, b: Vector3, scale: float) -> Vector3:
    return Vector3(a.x + b.x * scale, a.y + b.y * scale, a.z + b.z * scale)


def _norm(a: Vector3) -> float:
    return sqrt(_dot(a, a))


class GeometryInteractionEvaluator:
    """Evaluate a finite path against one explicit rectangular plate frame."""

    OPERATION_ID = "finite_path_planar_rectangle_intersection"

    def evaluate(self, path: IncomingGeometricPath, plate: PlanarDeflectorReference, routing: DeclaredRouting, policy: GeometryInteractionPolicy) -> GeometryInteractionResult:
        """Return deterministic geometry/routing or a governed rejected result."""
        diagnostic = self._validate(path, plate, routing, policy)
        if diagnostic:
            classification = InteractionClassification.UNSUPPORTED_GEOMETRY if diagnostic.code == "GI_UNSUPPORTED_GEOMETRY" else InteractionClassification.INVALID_INPUT
            return self._result(path, plate, policy, classification, RoutingClassification.REJECTED, None, SurfaceRelationship.NONE, None, (diagnostic,), False)
        tolerance = policy.geometric_tolerance_m
        direction_tolerance = policy.direction_tolerance
        denominator = _dot(path.direction, plate.normal)
        plane_distance = _dot(_sub(plate.center, path.origin), plate.normal)
        if abs(denominator) <= direction_tolerance:
            if abs(plane_distance) <= tolerance:
                return self._result(path, plate, policy, InteractionClassification.COPLANAR_OR_AMBIGUOUS, RoutingClassification.UNAVAILABLE, None, SurfaceRelationship.AMBIGUOUS, None, (self._diag("GI_COPLANAR_AMBIGUOUS", "The path is coplanar with the deflector surface."),), False)
            return self._route(path, plate, policy, InteractionClassification.NO_INTERSECTION, None, SurfaceRelationship.NONE, routing)
        distance = plane_distance / denominator
        if distance < -tolerance or distance > path.extent_m + tolerance:
            return self._route(path, plate, policy, InteractionClassification.NO_INTERSECTION, None, SurfaceRelationship.NONE, routing)
        point = _add_scaled(path.origin, path.direction, distance)
        local = _sub(point, plate.center)
        width_position = _dot(local, plate.width_axis)
        insertion_position = _dot(local, plate.insertion_axis)
        half_width = plate.width_m / 2
        half_insertion = plate.insertion_length_m / 2
        if abs(width_position) > half_width + tolerance or abs(insertion_position) > half_insertion + tolerance:
            return self._route(path, plate, policy, InteractionClassification.NO_INTERSECTION, None, SurfaceRelationship.NONE, routing)
        on_width = abs(abs(width_position) - half_width) <= tolerance
        on_insertion = abs(abs(insertion_position) - half_insertion) <= tolerance
        if on_width and on_insertion:
            interaction, relationship = InteractionClassification.CORNER_INTERSECTION, SurfaceRelationship.CORNER
        elif on_width or on_insertion:
            interaction, relationship = InteractionClassification.EDGE_INTERSECTION, SurfaceRelationship.EDGE
        else:
            interaction = InteractionClassification.FACE_INTERSECTION
            relationship = SurfaceRelationship.FRONT_FACING if denominator < 0 else SurfaceRelationship.BACK_FACING
        if routing.blocked:
            interaction = InteractionClassification.BLOCKED_BY_GEOMETRY
        return self._route(path, plate, policy, interaction, point, relationship, routing)

    def _route(self, path, plate, policy, interaction, point, relationship, routing):
        if routing.blocked and interaction is not InteractionClassification.NO_INTERSECTION:
            return self._result(path, plate, policy, InteractionClassification.BLOCKED_BY_GEOMETRY, RoutingClassification.TERMINATE_DUE_TO_BLOCKAGE, point, relationship, None, (), True)
        selected = routing.continue_cv_id if interaction is InteractionClassification.NO_INTERSECTION else routing.redirected_cv_id
        outcome = RoutingClassification.CONTINUE_DECLARED_PATH if interaction is InteractionClassification.NO_INTERSECTION else RoutingClassification.REDIRECT_TO_DECLARED_DOWNSTREAM_CV
        if selected is None:
            return self._result(path, plate, policy, interaction, RoutingClassification.UNAVAILABLE, point, relationship, None, (self._diag("GI_DOWNSTREAM_RELATIONSHIP_MISSING", "No explicit downstream relationship is available."),), False)
        if selected not in routing.valid_downstream_cv_ids:
            return self._result(path, plate, policy, interaction, RoutingClassification.REJECTED, point, relationship, None, (self._diag("GI_UNDECLARED_DOWNSTREAM_CV", "Routing selected an undeclared downstream control volume."),), False)
        return self._result(path, plate, policy, interaction, outcome, point, relationship, selected, (), True)

    def _validate(self, path, plate, routing, policy):
        values = (*path.origin.__dict__.values(), *path.direction.__dict__.values()) if hasattr(path.origin, "__dict__") else (path.origin.x, path.origin.y, path.origin.z, path.direction.x, path.direction.y, path.direction.z)
        if not path.path_id or not all(isfinite(v) for v in values) or _norm(path.direction) == 0 or not isfinite(path.extent_m) or path.extent_m <= 0:
            return self._diag("GI_INVALID_PATH", "The incoming geometric path is invalid.")
        if plate.geometry_kind != "planar_rectangle":
            return self._diag("GI_UNSUPPORTED_GEOMETRY", "Only an explicit planar rectangular deflector is supported.", DiagnosticSeverity.OUTSIDE_ENVELOPE)
        vectors = (plate.normal, plate.width_axis, plate.insertion_axis)
        plate_scalars = (plate.center.x, plate.center.y, plate.center.z, plate.width_m, plate.insertion_length_m, *(component for vector in vectors for component in (vector.x, vector.y, vector.z)))
        if not plate.deflector_id or not plate.surface_id or not all(isfinite(v) for v in plate_scalars) or any(_norm(v) == 0 for v in vectors) or plate.width_m <= 0 or plate.insertion_length_m <= 0:
            return self._diag("GI_INVALID_DEFLECTOR", "The deflector geometry frame is invalid.")
        t = policy.geometric_tolerance_m
        d = policy.direction_tolerance
        if not isfinite(t) or t <= 0 or not isfinite(d) or d <= 0 or not policy.evaluator_version:
            return self._diag("GI_INVALID_POLICY", "Explicit positive geometric and direction tolerances plus evaluator version are required.")
        if abs(_norm(path.direction) - 1) > d or any(abs(_norm(v) - 1) > d for v in vectors) or abs(_dot(plate.normal, plate.width_axis)) > d or abs(_dot(plate.normal, plate.insertion_axis)) > d or abs(_dot(plate.width_axis, plate.insertion_axis)) > d:
            return self._diag("GI_INVALID_FRAME", "Path direction and deflector axes must be explicit orthonormal unit vectors.")
        if len(set(routing.valid_downstream_cv_ids)) != len(routing.valid_downstream_cv_ids):
            return self._diag("GI_INVALID_ROUTING", "Declared downstream control-volume identifiers must be unique.")
        return None

    @staticmethod
    def _diag(code, message, severity=DiagnosticSeverity.BLOCKING_INPUT):
        return Diagnostic(code, severity, "geometry_interaction", message)

    def _result(self, path, plate, policy, interaction, routing, point, relationship, selected, diagnostics, available):
        provenance = InteractionProvenance(path.path_id, plate.deflector_id, plate.surface_id, self.OPERATION_ID, interaction.value, selected, policy.evaluator_version)
        return GeometryInteractionResult(interaction, routing, point, plate.surface_id if point else None, plate.normal if point else None, relationship, selected, provenance, diagnostics, available)


class GeometryInteractionStateAdapter:
    """Adapt the evaluator to the existing DeflectorInteraction state interface."""

    def __init__(self, evaluator, path, plate, routing, policy):
        self._evaluator, self._path, self._plate, self._routing, self._policy = evaluator, path, plate, routing, policy
        self.last_result: GeometryInteractionResult | None = None

    def evaluate(self, incoming: SegmentState, geometry_reference: str) -> SegmentState:
        """Create a candidate state without mutating the accepted incoming state."""
        if geometry_reference != self._plate.deflector_id:
            raise ValueError("deflector geometry reference does not match evaluator input")
        result = self._evaluator.evaluate(self._path, self._plate, self._routing, self._policy)
        self.last_result = result
        if not result.available:
            raise ValueError("geometry interaction evaluation unavailable or rejected")
        target = result.selected_downstream_cv_id or incoming.node_id
        return SegmentState(target, incoming.remaining_flow, incoming.pressure, incoming.momentum_direction)
