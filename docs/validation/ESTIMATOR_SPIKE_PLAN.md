# Estimator Technical Spike Plan

Status: Draft for Sprint 1.5 review

## Objective

Determine whether a parcel/ray model or influence-matrix model can support ADD's primary field decision: improving a biased 2 × 4 eight-cell outlet, typically observed as four usable and four very weak cells, by selecting an internal guide plate's position, insertion length, width, and angle. The model must provide useful, deterministic, explainable candidate ordering within V1's rectangular geometry envelope. This is isolated exploratory work, not production application code.

The spike must conform to `SOLVER_SPEC_V0.1.md`. In particular, cells cannot be scored independently: each extraction reduces the downstream mass basis, while residual direction, redirected momentum, pressure/resistance state where supported, and solver residuals propagate to subsequent cells.

## Time box and stop rule

Time-box implementation and evaluation to ten engineering days after benchmark inputs are accepted. If neither approach meets the agreed usefulness criteria, do not disguise failure with animation or tune against one case; document the gap and investigate new evidence or a different reduced-order approach.

## Shared scope

- One rectangular plenum and rectangular outlet grid.
- One inlet.
- Zero or one planar rectangular deflector.
- One immutable, SI-normalized JSON input format.
- Deterministic relative distribution per active cell.
- Explicit deflector position, insertion length, width, and angle.
- Causal accounting for estimated intercepted relative flow and redirected allocation.
- Sequential cell extraction with remaining-flow bookkeeping.
- Explicit mass, momentum, cell-flow, and pressure residuals where the prototype solves the corresponding state.
- Explicit `unavailable` output rather than invented physical inputs, coefficients, pressure, or absolute flow.
- No production persistence, authentication, final API/UI, optimization, or polished Three.js animation.

## Models

### A — Parcel/ray

Deterministically sample weighted parcels at the inlet, propagate/intersect them with simplified boundaries and a deflector, apply explicit spreading/attenuation rules, and accumulate outlet-cell contributions.

### B — Influence matrix

Compute cell influence weights from inlet direction, distance, geometry visibility, and deflector-dependent transfer terms, then normalize the resulting cell vector.

Both models must expose their factors well enough to explain why a cell changed.

## Benchmark cases

1. Symmetric synthetic case: preserves expected cell symmetry.
2. Intentionally biased inlet: produces directional imbalance and responds continuously to inlet movement.
3. **Primary V1 eight-cell case:** a 2 × 4 outlet with a strongly biased inlet and approximately four usable/four weak cells. Test multiple plate positions, insertion lengths, widths, and angles. At least one candidate should attempt to improve the weak group while tracking loss in the strong group.
4. Deflector sensitivity cases: vary one plate parameter at a time and identify discontinuities, non-causal behavior, or unreliable regions.
5. Measured field case: use the primary geometry pattern when available and include test conditions, instrument metadata, eight-cell measurements, and candidate ordering.

Inputs and expected invariants are reviewed before tuning. Measured data is held separately from model output.

## Required outputs for the primary case

1. Baseline relative share for each of the eight cells.
2. Candidate relative share for each of the eight cells.
3. Candidate-minus-baseline change per cell in percentage points.
4. Weak-cell improvement summary for the observed four-cell weak set.
5. Strong-cell reduction summary for the previously usable four-cell set.
6. Estimated intercepted-flow fraction with an explicit model-estimate label.
7. Estimated redirected-flow allocation across the eight cells.
8. Reliability warnings triggered by geometry, assumptions, sensitivity, or validation-envelope limits.

The prototypes must expose how the causal chain—biased inlet, plate interaction, interception, redirection, and outlet redistribution—produced these values. A model that only changes cell scores without an explainable deflector interaction does not meet the spike objective.

## Evaluation matrix

| Criterion | Evidence |
|---|---|
| Determinism | Repeated runs produce identical outputs |
| Symmetry | Mirrored/symmetric inputs preserve corresponding outputs |
| Runtime | Median and p95 on the reference machine |
| Explainability | Per-cell factor/contribution trace and engineer review |
| Geometry sensitivity | Controlled parameter sweeps are continuous and directionally plausible |
| Calibration | Number/meaning of tunable parameters and cross-case stability |
| Candidate ordering | Agreement with measured improvement ordering, not visual resemblance |
| Visualization suitability | Paths/contributions can support a conceptual view without driving model selection |
| Weak/strong trade-off | Improves the defined weak set while quantifying reduction in the strong set |
| Causal accounting | Intercepted estimate and redirected cell allocation reconcile under documented model rules |
| Conservation | Global and station-level mass bookkeeping closes within the configured criterion |
| Sequential propagation | Upstream extraction changes the available downstream state and is auditable per cell |
| Convergence | Iteration status and every enabled residual are reported explicitly |
| Physical provenance | Equations, coefficients, inputs, and applicability ranges are cited or marked unavailable |

Numeric acceptance thresholds require Product Owner and engineering-domain approval before results are evaluated. Avoid inventing a combined score that hides a critical failure.

## Deliverables

- This plan.
- `ESTIMATOR_SPIKE_RESULTS.md` completed after execution.
- Two disposable implementations in isolated prototype directories.
- Versioned benchmark input snapshots and outputs.
- Reproducible benchmark command and environment notes.
- Recommendation: parcel/ray, influence matrix, neither, or further investigation, with supported envelope and limitations.

## Decision rule

Choose the simplest model that satisfies all mandatory usefulness and integrity criteria. More attractive paths, more parameters, or closer fit to a single tuned case are not sufficient reasons.
