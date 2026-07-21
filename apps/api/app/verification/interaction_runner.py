"""Canonical geometry-interaction verification and golden runner."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from app.solver.geometry import Vector3
from app.solver.geometry_interaction import DeclaredRouting, GeometryInteractionEvaluator, GeometryInteractionPolicy, IncomingGeometricPath, PlanarDeflectorReference

from .golden import compare_golden, update_golden


@dataclass(frozen=True, slots=True)
class InteractionCase:
    """One explicit physics-free geometry contract case."""
    case_id: str
    path: IncomingGeometricPath
    plate: PlanarDeflectorReference
    routing: DeclaredRouting
    policy: GeometryInteractionPolicy
    expected_interaction: str
    expected_routing: str
    expected_available: bool


def canonical_interaction_cases() -> tuple[InteractionCase, ...]:
    """Return deterministic cases with explicit geometry and routing."""
    p = GeometryInteractionPolicy(0.000001, 0.000001, "geometry-interaction-v0.1")
    plate = PlanarDeflectorReference("D1", "D1:face", Vector3(0, 0, 0), Vector3(0, 0, 1), Vector3(1, 0, 0), Vector3(0, 1, 0), 2, 2)
    routes = DeclaredRouting(("CV_CONTINUE", "CV_REDIRECT"), "CV_CONTINUE", "CV_REDIRECT", False)
    return (
        InteractionCase("clear-no-intersection", IncomingGeometricPath("P1", Vector3(2, 0, 1), Vector3(0, 0, -1), 2), plate, routes, p, "no_intersection", "continue_declared_path", True),
        InteractionCase("face-intersection", IncomingGeometricPath("P2", Vector3(0, 0, 1), Vector3(0, 0, -1), 2), plate, routes, p, "face_intersection", "redirect_to_declared_downstream_cv", True),
        InteractionCase("edge-intersection", IncomingGeometricPath("P3", Vector3(1, 0, 1), Vector3(0, 0, -1), 2), plate, routes, p, "edge_intersection", "redirect_to_declared_downstream_cv", True),
        InteractionCase("corner-intersection", IncomingGeometricPath("P4", Vector3(1, 1, 1), Vector3(0, 0, -1), 2), plate, routes, p, "corner_intersection", "redirect_to_declared_downstream_cv", True),
        InteractionCase("coplanar-ambiguous", IncomingGeometricPath("P5", Vector3(0, 0, 0), Vector3(1, 0, 0), 2), plate, routes, p, "coplanar_or_ambiguous", "unavailable", False),
        InteractionCase("invalid-path", IncomingGeometricPath("P6", Vector3(0, 0, 1), Vector3(0, 0, 0), 2), plate, routes, p, "invalid_input", "rejected", False),
        InteractionCase("invalid-deflector", IncomingGeometricPath("P7", Vector3(0, 0, 1), Vector3(0, 0, -1), 2), PlanarDeflectorReference("D1", "D1:face", Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(1, 0, 0), Vector3(0, 1, 0), 2, 2), routes, p, "invalid_input", "rejected", False),
        InteractionCase("unsupported-geometry", IncomingGeometricPath("P8", Vector3(0, 0, 1), Vector3(0, 0, -1), 2), PlanarDeflectorReference("D1", "D1:face", Vector3(0, 0, 0), Vector3(0, 0, 1), Vector3(1, 0, 0), Vector3(0, 1, 0), 2, 2, "mesh"), routes, p, "unsupported_geometry", "rejected", False),
        InteractionCase("missing-downstream", IncomingGeometricPath("P9", Vector3(0, 0, 1), Vector3(0, 0, -1), 2), plate, DeclaredRouting(("CV_CONTINUE",), "CV_CONTINUE", None, False), p, "face_intersection", "unavailable", False),
        InteractionCase("declared-downstream", IncomingGeometricPath("P10", Vector3(0, 0, 1), Vector3(0, 0, -1), 2), plate, routes, p, "face_intersection", "redirect_to_declared_downstream_cv", True),
        InteractionCase("blocked-geometry", IncomingGeometricPath("P11", Vector3(0, 0, 1), Vector3(0, 0, -1), 2), plate, DeclaredRouting(("CV_CONTINUE",), "CV_CONTINUE", None, True), p, "blocked_by_geometry", "terminate_due_to_blockage", True),
    )


def result_payload(case: InteractionCase) -> dict[str, object]:
    """Execute and serialize geometric contract without engineering magnitudes."""
    result = GeometryInteractionEvaluator().evaluate(case.path, case.plate, case.routing, case.policy)
    point = None if result.intersection_point is None else {"x": result.intersection_point.x, "y": result.intersection_point.y, "z": result.intersection_point.z}
    return {"case_id": case.case_id, "interaction": result.interaction.value, "routing": result.routing.value, "available": result.available, "intersection_point": point, "surface_id": result.surface_id, "surface_relationship": result.surface_relationship.value, "selected_downstream_cv_id": result.selected_downstream_cv_id, "diagnostics": [item.code for item in result.diagnostics], "provenance": {"path_id": result.provenance.path_id, "deflector_id": result.provenance.deflector_id, "surface_id": result.provenance.surface_id, "operation_id": result.provenance.operation_id, "rule_id": result.provenance.classification_rule_id, "selected_relationship": result.provenance.selected_relationship, "evaluator_version": result.provenance.evaluator_version}, "recommendation": None, "engineering_magnitudes": {}}


def run(golden_dir: Path, *, update: bool = False, confirmed: bool = False) -> int:
    """Run canonical interaction contracts and return non-zero on regression."""
    failed = 0
    for case in canonical_interaction_cases():
        payload = result_payload(case)
        failures = []
        for field, expected in (("interaction", case.expected_interaction), ("routing", case.expected_routing), ("available", case.expected_available)):
            if payload[field] != expected:
                failures.append(f"{field}: expected {expected!r}, got {payload[field]!r}")
        path = golden_dir / f"{case.case_id}.json"
        if update:
            update_golden(path, payload, confirmed=confirmed)
        else:
            matches, diff = compare_golden(path, payload)
            if not matches:
                failures.append("golden mismatch\n" + diff)
        if failures:
            failed += 1
            print(f"FAIL {case.case_id} [geometry contract regression]")
            for item in failures: print(f"  {item}")
        else:
            print(f"PASS {case.case_id}")
    print(f"SUMMARY pass={len(canonical_interaction_cases()) - failed} fail={failed}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goldens", type=Path, default=Path("verification/interaction_goldens"))
    parser.add_argument("--update-golden", action="store_true")
    parser.add_argument("--confirm-update", action="store_true")
    args = parser.parse_args()
    if args.confirm_update and not args.update_golden: parser.error("--confirm-update requires --update-golden")
    return run(args.goldens, update=args.update_golden, confirmed=args.confirm_update)


if __name__ == "__main__": raise SystemExit(main())
