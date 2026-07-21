# Sprint 1.7 Geometry Interaction Report

Status: Complete — governed geometry evaluator baseline

## Implemented architecture

- Immutable path, planar-deflector frame, declared-routing, policy, result, provenance, and diagnostic contracts.
- Deterministic finite-path/planar-rectangle evaluator with no HVAC calculations.
- Explicit dimensional geometry tolerance and separate dimensionless direction tolerance; neither has a default.
- State-engine adapter implementing the existing deflector interaction protocol. It creates candidate state only, preserves all incoming engineering-value objects, and raises on unavailable/rejected evaluation.
- Dedicated interaction regression runner and deterministic golden snapshots using the Sprint 1.6 golden policy.
- Interaction verification tests and timing-only benchmark extensions.

## Supported geometry

One finite explicit unit-direction path and one zero-thickness planar rectangular deflector described by center, normal, orthogonal width/insertion axes, width, and insertion length in the canonical SI frame. Routing selects only explicitly declared downstream CV IDs.

Unsupported shapes, missing axes/direction/extent/tolerances, non-orthonormal frames, invalid dimensions, coplanar ambiguity, and undeclared routing are rejected or unavailable. They are never approximated or repaired.

## Interaction classifications

`no_intersection`, `face_intersection`, `edge_intersection`, `corner_intersection`, `coplanar_or_ambiguous`, `blocked_by_geometry`, `unsupported_geometry`, and `invalid_input`.

Surface relationships are geometric only: `front_facing`, `back_facing`, `edge`, `corner`, `ambiguous`, and `none`.

## Routing classifications

`continue_declared_path`, `redirect_to_declared_downstream_cv`, `terminate_due_to_blockage`, `unavailable`, and `rejected`.

“Redirect” selects an existing declared graph relationship. It does not calculate aerodynamic direction or performance.

## Case and golden inventory

Eleven deterministic golden cases:

1. Clear no-intersection.
2. Face intersection.
3. Edge intersection.
4. Corner intersection.
5. Coplanar ambiguity.
6. Invalid path.
7. Invalid deflector frame.
8. Unsupported geometry.
9. Missing downstream relationship.
10. Valid declared downstream selection.
11. Explicit blocked geometry.

Additional property/integration tests cover deterministic repeatability, provenance preservation, undeclared CV rejection, absence of engineering magnitudes/recommendations, candidate rejection, accepted-state isolation, and failed-result visualization isolation.

## Verification results

- Complete project compilation succeeds.
- All Sprint 1.5, 1.6, and 1.7 tests pass.
- Sprint 1.6 regression runner passes all twelve framework cases.
- Sprint 1.7 runner passes all eleven interaction cases.
- A temporary deliberately corrupted face-intersection golden produces a unified diff and non-zero runner result.
- Unsupported geometry deterministically returns `unsupported_geometry` plus rejected routing.
- Unconfirmed golden writes remain prohibited by the shared policy.

## Benchmark policy

The standard-library harness now times path/deflector evaluation, surface classification access, routing classification access, and provenance packaging in addition to prior framework stages. Results are environment-tagged timing observations only, with no pass/fail threshold or engineering implication.

## Known limitations

- The path is a geometric line, not a streamline or stream tube.
- Plate thickness and surrounding solid obstructions are not modeled.
- Coplanar overlap remains ambiguous.
- Only one path and one planar rectangle are supported.
- The evaluator does not derive incoming direction or downstream topology.
- Floating-point boundary classification depends on explicit reviewed computational tolerances.
- Blocking is explicitly declared; it is not inferred from a solid-scene model.

## Unresolved engineering questions

- Which upstream component supplies/validates geometric path direction in later sprints?
- How is the declared downstream relationship authored and reviewed for field geometry?
- Should plate thickness and non-face boundary features enter the next geometry envelope?
- What governance selects computational geometry tolerances for production datasets?
- When multiple valid downstream branches exist, which separate reviewed routing capability owns selection?

## Sprint 1.8 entry criteria

- This specification/report and tolerance separation are accepted.
- Source and governance of incoming geometric paths are approved.
- Any expanded geometry primitive has its own applicability and verification plan.
- No aerodynamic interpretation is added without HVAC-domain review.
- New golden expectations remain geometric and provenance-bearing.
- Existing failure isolation and no-recommendation invariants remain mandatory.

## Validation statement

**Sprint 1.7 validates deterministic geometry classification and declared topological routing contracts only. No airflow magnitude, distribution, pressure, resistance, extraction, loss, turbulence, aerodynamic deflection, performance, or HVAC physics has been validated.**
