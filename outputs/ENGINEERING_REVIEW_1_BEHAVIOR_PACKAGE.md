# ADD Engineering Review 1 — Experimental Airflow Solver V0.1

Review date: 2026-07-22  
Purpose: inspect current solver behavior only  
Claim level: experimental, unvalidated HVAC behavior

## Review controls

- Behavior Fix 1 changed only empty-deflector acceptance and allocation-to-sequential handoff; experimental airflow assumptions and geometric influence formulas were not changed.
- Values below are direct outputs from the current public `ExperimentalAirflowSolver.solve()` path.
- No rejected case was replaced by an internal-kernel or hand-calculated result.
- Displayed values are rounded for readability; conservation statements use the solver's unrounded outputs.
- Bar scale for completed cases: approximately one `█` per percentage point.

## Shared geometry

| Component | Geometry |
|---|---|
| Plenum | Rectangular, 4.0 m length × 2.0 m width × 2.0 m height |
| Coordinate domain | X: −2.0…+2.0 m; Y: −1.0…+1.0 m; Z: 0…2.0 m |
| Inlet | Center `(0, 0, 2.0)` m; 0.4 × 0.4 m; direction `(0, 0, −1)`; supplied total 800 CFM |
| Outlet size | Eight outlets, each 0.3 × 0.3 m, on Z = 0 plane |
| Bottom row | R0C0 `(-1.5, -0.4, 0)`; R0C1 `(-0.5, -0.4, 0)`; R0C2 `(0.5, -0.4, 0)`; R0C3 `(1.5, -0.4, 0)` |
| Top row | R1C0 `(-1.5, 0.4, 0)`; R1C1 `(-0.5, 0.4, 0)`; R1C2 `(0.5, 0.4, 0)`; R1C3 `(1.5, 0.4, 0)` |

The current geometry is symmetric in Y, so all completed cases produce equal results between corresponding top and bottom cells.

## Case 1 — No deflector

### Geometry

Shared plenum, inlet, and eight outlets with an empty deflector collection.

### Solver result

| Outlet | Percentage | Estimated airflow |
|---|---:|---:|
| R0C0 | 9.08% | 72.66 CFM |
| R0C1 | 15.92% | 127.34 CFM |
| R0C2 | 15.92% | 127.34 CFM |
| R0C3 | 9.08% | 72.66 CFM |
| R1C0 | 9.08% | 72.66 CFM |
| R1C1 | 15.92% | 127.34 CFM |
| R1C2 | 15.92% | 127.34 CFM |
| R1C3 | 9.08% | 72.66 CFM |

```text
R0C0   9.08%  █████████
R0C1  15.92%  ████████████████
R0C2  15.92%  ████████████████
R0C3   9.08%  █████████
R1C0   9.08%  █████████
R1C1  15.92%  ████████████████
R1C2  15.92%  ████████████████
R1C3   9.08%  █████████
```

### Total airflow verification

- Supplied inlet: 800 CFM
- Estimated outlet total: 800 CFM
- Terminal remaining: 0 CFM
- Conservation residual: 0 CFM
- Solver conservation result: `true`

### Behavior explanation

With no deflector, the solver uses only the existing directional area/distance baseline kernel. The inlet and outlet grid are centered and symmetric, so corresponding top/bottom cells match. The two inner columns are closer to the inlet center and therefore receive higher inverse-distance weights than the two outer columns. No redirected-flow influence or virtual deflector is applied.

## Case 2 — One deflector at 30°

### Geometry

D1 center `(0, 0, 1.0)` m; width 0.2 m; height 0.2 m; angle +30° about global +Y. Solver audit: normal approximately `(0.5000, 0, 0.8660)`, projected area 0.034641 m², experimental intercepted-fraction proxy 0.216506.

### Distribution

| Outlet | Percentage | Estimated airflow |
|---|---:|---:|
| R0C0 | 7.12% | 56.93 CFM |
| R0C1 | 12.47% | 99.77 CFM |
| R0C2 | 12.47% | 99.77 CFM |
| R0C3 | 17.94% | 143.53 CFM |
| R1C0 | 7.12% | 56.93 CFM |
| R1C1 | 12.47% | 99.77 CFM |
| R1C2 | 12.47% | 99.77 CFM |
| R1C3 | 17.94% | 143.53 CFM |

```text
R0C0   7.12%  ███████
R0C1  12.47%  ████████████
R0C2  12.47%  ████████████
R0C3  17.94%  ██████████████████
R1C0   7.12%  ███████
R1C1  12.47%  ████████████
R1C2  12.47%  ████████████
R1C3  17.94%  ██████████████████
```

### Total airflow verification

- Supplied inlet: 800 CFM
- Estimated outlet total: 799.9999999999999 CFM
- Terminal remaining: 0 CFM
- Conservation residual: approximately `1.14 × 10⁻¹³` CFM
- Solver conservation result: `true`

### Behavior explanation

At 30°, the experimental projected-area proxy is the largest of the three single-deflector review angles. The geometric reflection proxy points influence toward positive X. Consequently, the rightmost outlets receive the highest weights, the two middle columns remain equal in this geometry, and the leftmost outlets receive the least. The identical top/bottom values follow from Y symmetry.

## Case 3 — One deflector at 45°

### Geometry

D1 center `(0, 0, 1.0)` m; width 0.2 m; height 0.2 m; angle +45° about global +Y. Solver audit: normal approximately `(0.7071, 0, 0.7071)`, projected area 0.028284 m², experimental intercepted-fraction proxy 0.176777.

### Distribution

| Outlet | Percentage | Estimated airflow |
|---|---:|---:|
| R0C0 | 7.48% | 59.82 CFM |
| R0C1 | 13.10% | 104.83 CFM |
| R0C2 | 18.02% | 144.16 CFM |
| R0C3 | 11.40% | 91.19 CFM |
| R1C0 | 7.48% | 59.82 CFM |
| R1C1 | 13.10% | 104.83 CFM |
| R1C2 | 18.02% | 144.16 CFM |
| R1C3 | 11.40% | 91.19 CFM |

```text
R0C0   7.48%  ███████
R0C1  13.10%  █████████████
R0C2  18.02%  ██████████████████
R0C3  11.40%  ███████████
R1C0   7.48%  ███████
R1C1  13.10%  █████████████
R1C2  18.02%  ██████████████████
R1C3  11.40%  ███████████
```

### Total airflow verification

- Supplied inlet: 800 CFM
- Estimated outlet total: 799.9999999999999 CFM
- Terminal remaining: 0 CFM
- Conservation residual: approximately `1.14 × 10⁻¹³` CFM
- Solver conservation result: `true`

### Behavior explanation

The 45° reflection proxy points primarily across +X rather than directly toward the outlet plane. From the centered deflector location, the positive-X inner column R0C2/R1C2 has the strongest combined alignment and distance weight. The far-right column remains influenced but is penalized by distance, so it falls below the inner-right column. The leftmost column remains weakest.

## Case 4 — One deflector at 60°

### Geometry

D1 center `(0, 0, 1.0)` m; width 0.2 m; height 0.2 m; angle +60° about global +Y. Solver audit: normal approximately `(0.8660, 0, 0.5000)`, projected area 0.020000 m², experimental intercepted-fraction proxy 0.125000. All other geometry is unchanged.

### Solver result

| Outlet | Percentage | Estimated airflow |
|---|---:|---:|
| R0C0 | 7.95% | 63.58 CFM |
| R0C1 | 14.21% | 113.68 CFM |
| R0C2 | 17.87% | 142.97 CFM |
| R0C3 | 9.97% | 79.76 CFM |
| R1C0 | 7.95% | 63.58 CFM |
| R1C1 | 14.21% | 113.68 CFM |
| R1C2 | 17.87% | 142.97 CFM |
| R1C3 | 9.97% | 79.76 CFM |

```text
R0C0   7.95%  ████████
R0C1  14.21%  ██████████████
R0C2  17.87%  ██████████████████
R0C3   9.97%  ██████████
R1C0   7.95%  ████████
R1C1  14.21%  ██████████████
R1C2  17.87%  ██████████████████
R1C3   9.97%  ██████████
```

### Total airflow verification

- Supplied inlet: 800 CFM
- Estimated outlet total: 800.0000000000001 CFM
- Terminal remaining: 0 CFM
- Conservation residual: approximately `−1.14 × 10⁻¹³` CFM
- Solver conservation result: `true`

### Behavior explanation

At 60°, the projected interception proxy is smaller than at 30° and the reflected direction changes the distance/alignment balance. The inner-right R0C2/R1C2 cells remain strongest, followed by the inner-left cells. The corrected handoff now derives every extraction from the same accepted remaining state used by sequential accounting, so the strict guard completes without changing the geometric influence model.

## Case 5 — Two deflectors

### Geometry

- D1: center `(0, 0, 1.0)` m; 0.2 × 0.2 m; +45° about +Y.
- D2: center `(0.5, 0, 0.8)` m; 0.15 × 0.2 m; −45° about +Y.

Solver audit:

- D1 projected area 0.028284 m²; intercepted proxy 0.176777.
- D2 projected area 0.021213 m²; intercepted proxy 0.132583.

### Distribution

| Outlet | Percentage | Estimated airflow |
|---|---:|---:|
| R0C0 | 8.57% | 68.58 CFM |
| R0C1 | 15.91% | 127.27 CFM |
| R0C2 | 15.63% | 125.05 CFM |
| R0C3 | 9.89% | 79.10 CFM |
| R1C0 | 8.57% | 68.58 CFM |
| R1C1 | 15.91% | 127.27 CFM |
| R1C2 | 15.63% | 125.05 CFM |
| R1C3 | 9.89% | 79.10 CFM |

```text
R0C0   8.57%  █████████
R0C1  15.91%  ████████████████
R0C2  15.63%  ████████████████
R0C3   9.89%  ██████████
R1C0   8.57%  █████████
R1C1  15.91%  ████████████████
R1C2  15.63%  ████████████████
R1C3   9.89%  ██████████
```

### Total airflow verification

- Supplied inlet: 800 CFM
- Estimated outlet total: 800 CFM
- Terminal remaining: 0 CFM
- Conservation residual: 0 CFM
- Solver conservation result: `true`

### Behavior explanation

The solver applies deflectors sequentially in input order. D1 shifts influence toward positive X; D2, positioned on the positive-X side with a negative angle, introduces an opposing reflected proxy. Their sequential mixture concentrates the result in the two inner columns and reduces both outer columns. R0C1/R1C1 are slightly higher than R0C2/R1C2 because D2 is offset to X = 0.5 m and its negative-angle proxy changes the final distance/alignment balance.

## Cross-case observations

1. The solver now provides a true no-deflector baseline using only the existing baseline kernel.
2. Deflector angle changes both the projected interception proxy and reflected direction, so changes are non-monotonic by outlet.
3. Deflector position materially affects the distance/alignment weighting.
4. Y-symmetric inputs produce Y-symmetric top/bottom results.
5. Completed cases conserve the supplied 800 CFM within the explicitly configured numerical comparison.
6. The corrected 60° handoff completes without relaxing the sequential over-extraction guard.
7. These patterns describe the current algorithm, not validated airflow physics.

## Review questions

- Is Y symmetry expected for the intended field geometry, or should inlet/off-axis geometry be included in the next review set?
- Do the 30°, 45°, and two-deflector qualitative shifts agree with engineer expectations strongly enough to justify calibration experiments?

## Behavior Fix 1 — Before versus after

### No-deflector baseline

- Before: rejected during input validation with `at least one deflector is required`; no outlet payload.
- After: accepted with an empty deflector tuple; only the unchanged baseline allocation kernel runs; total is 800 CFM and residual is zero.
- Assumptions changed: none. The obsolete execution restriction was removed.

### 60° sequential handoff

- Before: candidate distribution was rejected with `SE_EXTRACTION_EXCEEDS_INCOMING` because allocation generation and sequential subtraction followed slightly different floating-point remaining paths.
- After: each instruction is computed as the current accepted remaining amount minus the next cumulative-share target, and that exact subtraction updates the next remaining amount. All eight steps stay within their available incoming quantity.
- Geometric influence changed: no. Projected-area, reflection, distance/alignment weighting, normalization, labels, and provenance are unchanged.
- Safety rule changed: no. Over-extraction remains strictly rejected; no clipping or correction coefficient was introduced.

## Mandatory interpretation

The reported CFM values are experimental allocations of the supplied 800 CFM. They are not validated outlet airflow predictions and must not be used for fabrication, balancing, compliance, or field acceptance.
