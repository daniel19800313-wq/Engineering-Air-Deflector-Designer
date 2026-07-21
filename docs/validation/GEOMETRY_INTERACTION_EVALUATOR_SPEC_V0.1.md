# Geometry Interaction Evaluator Specification V0.1

Status: Sprint 1.7 governed geometry specification

## Purpose and scope

Determine deterministic geometric intersection, surface orientation, and selection among explicitly declared downstream control-volume relationships. The evaluator connects the Geometry Engine to the existing candidate-state workflow without calculating any airflow physics.

## Inputs

- Finite incoming geometric path: stable ID, canonical-SI origin, explicit unit direction, and explicit geometric extent.
- Rectangular planar deflector reference: stable deflector/surface IDs, center, unit normal, explicit orthogonal width/insertion axes, width, and insertion length.
- Declared routing: complete set of valid downstream CV IDs, optional continue relationship, optional redirected relationship, and explicit blockage declaration.
- Policy: caller-supplied positive geometric-distance tolerance in metres, positive dimensionless direction/orthogonality tolerance, and evaluator version. There are no default tolerances, and dimensioned/dimensionless tolerances are not interchangeable.

Missing geometry, axes, direction, extent, routing, or policy is never inferred or repaired.

## Outputs

Immutable result containing interaction classification, routing classification, optional intersection point, surface ID/normal, geometric surface relationship, selected declared CV, provenance, diagnostics, and availability. It contains no engineering magnitude.

## Coordinate-system assumptions

All inputs use the approved canonical right-handed SI frame. Direction and plate-frame axes are explicit orthonormal unit vectors. The evaluator validates rather than normalizes them because automatic normalization could hide invalid input.

## Geometric primitives

- Finite directed line path.
- One planar rectangle defined by center, normal, two in-plane axes, and extents.
- One explicit set of downstream CV identifiers and relationships.

No curves, thickness volume, arbitrary polygon, mesh, solid obstruction field, multiple plates, or multiple paths are supported.

## Interaction classifications

- `no_intersection`
- `face_intersection`
- `edge_intersection`
- `corner_intersection`
- `coplanar_or_ambiguous`
- `blocked_by_geometry`
- `unsupported_geometry`
- `invalid_input`

These are geometric labels only. They do not describe attachment, separation, turbulence, redirection efficiency, or aerodynamic behavior.

## Surface classifications

For an available point interaction, the result identifies the supplied surface and normal. The relationship is `front_facing`, `back_facing`, `edge`, `corner`, or `ambiguous`, based only on geometric incidence and boundary location. Pressure side and suction side are explicitly excluded.

## Routing classifications

- `continue_declared_path`: no intersection and explicit continue CV selected.
- `redirect_to_declared_downstream_cv`: geometric interaction and explicit redirected CV selected.
- `terminate_due_to_blockage`: caller explicitly declares the intersected geometry blocking.
- `unavailable`: geometry is ambiguous or a required declared relationship is absent.
- `rejected`: input, geometry, frame, or downstream selection is invalid/unsupported.

The evaluator cannot create, reorder, or infer a control volume and cannot infer outlet extraction.

## Provenance requirements

Every result records path, deflector and surface IDs; intersection operation ID; classification rule ID; selected relationship when available; and evaluator version. Rejected/unavailable results retain the same input/evaluator identity and stable diagnostic codes.

## Unavailable and failure contract

Coplanar geometry remains ambiguous. Missing downstream relationships remain unavailable. Undeclared CV selection, invalid paths/frames/dimensions/tolerance, mismatched state-adapter references, and unsupported shapes are rejected. A failed evaluation raises at the state adapter boundary, cannot mutate the accepted incoming state, and cannot enter visualization through a failed package.

## Applicability envelope

One finite path, one explicit planar rectangle, one orthonormal plate frame, and an explicitly declared linear downstream relationship set within the approved V0.1 coordinate convention. Computational tolerance is supplied and versioned by the verification/execution context; it is not an HVAC coefficient.

## Known limitations

- A line path is not an airflow stream tube or resolved trajectory.
- A zero-thickness plate surface does not model edge thickness or other obstruction volumes.
- Geometric “redirect” means selecting an already declared relationship, not calculating a new direction.
- Coplanar overlap is intentionally not resolved.
- Floating-point boundary classification depends on the explicitly supplied tolerance.
- The evaluator does not establish the physical validity of the supplied path or downstream topology.

## Verification strategy

Canonical cases cover no/face/edge/corner/coplanar interactions, invalid and unsupported inputs, blockage, missing/valid routing, determinism, provenance, candidate isolation, and failed-result visualization isolation. Goldens contain geometric contracts only. Property tests prohibit engineering magnitudes, undeclared routing, mutation, recommendations, and reinterpretation by visualization.

## Future extensions

Possible new versioned capabilities include finite-width incident regions, plate thickness/edge solids, multiple deflectors, multiple paths, arbitrary planar polygons, mesh intersection, and branched topology. Each requires an explicit interface version, applicability envelope, verification cases, and review; none changes V0.1 silently.

## Explicit exclusions

Airflow magnitude, velocity magnitude, pressure, resistance, extraction ratio, mass/momentum solution, turbulence, separation, loss, coefficients, physical deflection, performance, ranking, recommendation, CFD, optimization, and any absolute or relative airflow claim.
