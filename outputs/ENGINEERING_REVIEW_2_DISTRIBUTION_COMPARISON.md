# Engineering Review 2 — Distribution Comparison

## Review boundary

This report compares the corrected outputs of **Experimental Airflow Solver V0.1** for the five requested cases. Values below describe current deterministic solver behavior only. They do **not** establish physical validity, field accuracy, or design suitability. No solver code or golden dataset was changed for this review.

All cases use the same 800 CFM input and eight-outlet geometry. Percentages are shown to three decimal places, CFM to three decimal places, and differences are calculated against the unrounded no-deflector result. `Δ pp` means percentage-point difference from baseline.

## Case 1 — No deflector (baseline)

| Outlet ID | Airflow % | Airflow CFM | Δ pp | Δ CFM |
|---|---:|---:|---:|---:|
| R0C0 | 9.083 | 72.664 | 0.000 | 0.000 |
| R0C1 | 15.917 | 127.336 | 0.000 | 0.000 |
| R0C2 | 15.917 | 127.336 | 0.000 | 0.000 |
| R0C3 | 9.083 | 72.664 | 0.000 | 0.000 |
| R1C0 | 9.083 | 72.664 | 0.000 | 0.000 |
| R1C1 | 15.917 | 127.336 | 0.000 | 0.000 |
| R1C2 | 15.917 | 127.336 | 0.000 | 0.000 |
| R1C3 | 9.083 | 72.664 | 0.000 | 0.000 |

## Case 2 — One deflector at 30°

| Outlet ID | Airflow % | Airflow CFM | Δ pp | Δ CFM |
|---|---:|---:|---:|---:|
| R0C0 | 7.117 | 56.932 | -1.967 | -15.732 |
| R0C1 | 12.471 | 99.767 | -3.446 | -27.569 |
| R0C2 | 12.471 | 99.767 | -3.446 | -27.569 |
| R0C3 | 17.942 | 143.535 | +8.859 | +70.870 |
| R1C0 | 7.117 | 56.932 | -1.967 | -15.732 |
| R1C1 | 12.471 | 99.767 | -3.446 | -27.569 |
| R1C2 | 12.471 | 99.767 | -3.446 | -27.569 |
| R1C3 | 17.942 | 143.535 | +8.859 | +70.870 |

## Case 3 — One deflector at 45°

| Outlet ID | Airflow % | Airflow CFM | Δ pp | Δ CFM |
|---|---:|---:|---:|---:|
| R0C0 | 7.477 | 59.819 | -1.606 | -12.845 |
| R0C1 | 13.103 | 104.826 | -2.814 | -22.510 |
| R0C2 | 18.020 | 144.161 | +2.103 | +16.825 |
| R0C3 | 11.399 | 91.195 | +2.316 | +18.531 |
| R1C0 | 7.477 | 59.819 | -1.606 | -12.845 |
| R1C1 | 13.103 | 104.826 | -2.814 | -22.510 |
| R1C2 | 18.020 | 144.161 | +2.103 | +16.825 |
| R1C3 | 11.399 | 91.195 | +2.316 | +18.531 |

## Case 4 — One deflector at 60°

| Outlet ID | Airflow % | Airflow CFM | Δ pp | Δ CFM |
|---|---:|---:|---:|---:|
| R0C0 | 7.948 | 63.581 | -1.135 | -9.083 |
| R0C1 | 14.211 | 113.684 | -1.706 | -13.651 |
| R0C2 | 17.872 | 142.975 | +1.955 | +15.639 |
| R0C3 | 9.970 | 79.760 | +0.887 | +7.095 |
| R1C0 | 7.948 | 63.581 | -1.135 | -9.083 |
| R1C1 | 14.211 | 113.684 | -1.706 | -13.651 |
| R1C2 | 17.872 | 142.975 | +1.955 | +15.639 |
| R1C3 | 9.970 | 79.760 | +0.887 | +7.095 |

## Case 5 — Two deflectors

| Outlet ID | Airflow % | Airflow CFM | Δ pp | Δ CFM |
|---|---:|---:|---:|---:|
| R0C0 | 8.572 | 68.579 | -0.511 | -4.085 |
| R0C1 | 15.909 | 127.270 | -0.008 | -0.066 |
| R0C2 | 15.631 | 125.047 | -0.286 | -2.288 |
| R0C3 | 9.888 | 79.104 | +0.805 | +6.440 |
| R1C0 | 8.572 | 68.579 | -0.511 | -4.085 |
| R1C1 | 15.909 | 127.270 | -0.008 | -0.066 |
| R1C2 | 15.631 | 125.047 | -0.286 | -2.288 |
| R1C3 | 9.888 | 79.104 | +0.805 | +6.440 |

## Cross-case matrix

Each cell is `airflow % / CFM`.

| Case | R0C0 | R0C1 | R0C2 | R0C3 | R1C0 | R1C1 | R1C2 | R1C3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| No deflector | 9.083 / 72.664 | 15.917 / 127.336 | 15.917 / 127.336 | 9.083 / 72.664 | 9.083 / 72.664 | 15.917 / 127.336 | 15.917 / 127.336 | 9.083 / 72.664 |
| 30° | 7.117 / 56.932 | 12.471 / 99.767 | 12.471 / 99.767 | 17.942 / 143.535 | 7.117 / 56.932 | 12.471 / 99.767 | 12.471 / 99.767 | 17.942 / 143.535 |
| 45° | 7.477 / 59.819 | 13.103 / 104.826 | 18.020 / 144.161 | 11.399 / 91.195 | 7.477 / 59.819 | 13.103 / 104.826 | 18.020 / 144.161 | 11.399 / 91.195 |
| 60° | 7.948 / 63.581 | 14.211 / 113.684 | 17.872 / 142.975 | 9.970 / 79.760 | 7.948 / 63.581 | 14.211 / 113.684 | 17.872 / 142.975 | 9.970 / 79.760 |
| Two deflectors | 8.572 / 68.579 | 15.909 / 127.270 | 15.631 / 125.047 | 9.888 / 79.104 | 8.572 / 68.579 | 15.909 / 127.270 | 15.631 / 125.047 | 9.888 / 79.104 |

## Distribution statistics

Uniformity index is `minimum outlet airflow / maximum outlet airflow`. Because every case uses the same total flow, the ratio is identical whether calculated from CFM or percentage.

| Case | Maximum % | Minimum % | Spread (pp) | Uniformity index | Total CFM | Conservation residual CFM |
|---|---:|---:|---:|---:|---:|---:|
| No deflector | 15.917 | 9.083 | 6.834 | 0.571 | 800.000 | 0.000 |
| 30° | 17.942 | 7.117 | 10.825 | 0.397 | 800.000 | 0.000 |
| 45° | 18.020 | 7.477 | 10.543 | 0.415 | 800.000 | 0.000 |
| 60° | 17.872 | 7.948 | 9.924 | 0.445 | 800.000 | -0.000* |
| Two deflectors | 15.909 | 8.572 | 7.336 | 0.539 | 800.000 | 0.000 |

\* The unrounded 60° residual is a floating-point negative zero at the reported precision; its magnitude rounds to 0.000 CFM.

## Gain/loss inventory relative to baseline

| Case | Gaining outlets | Losing outlets | Unchanged outlets |
|---|---|---|---|
| No deflector | None | None | All eight |
| 30° | R0C3, R1C3 | R0C0, R0C1, R0C2, R1C0, R1C1, R1C2 | None |
| 45° | R0C2, R0C3, R1C2, R1C3 | R0C0, R0C1, R1C0, R1C1 | None |
| 60° | R0C2, R0C3, R1C2, R1C3 | R0C0, R0C1, R1C0, R1C1 | None |
| Two deflectors | R0C3, R1C3 | R0C0, R0C1, R0C2, R1C0, R1C1, R1C2 | None |

The two-deflector losses at R0C1 and R1C1 are only about 0.008 pp (0.066 CFM) each, but they remain numerically below baseline and are therefore classified as losses rather than unchanged.

## Observed behavior

### Angle sequence: 30° → 45° → 60°

Increasing angle does **not** produce one consistent monotonic trend across all outlets:

- R0C0/R1C0 and R0C1/R1C1 increase monotonically across 30°, 45°, and 60°.
- R0C3/R1C3 decrease monotonically.
- R0C2/R1C2 rise sharply from 30° to 45°, then fall slightly at 60°; these outlets are non-monotonic.
- The maximum shifts from column C3 at 30° to column C2 at 45° and remains at C2 at 60°.
- The spread narrows from 10.825 pp at 30° to 9.924 pp at 60°, while remaining wider than the 6.834 pp baseline spread.

Thus, the current solver shows structured directional movement with angle, but not a single consistent directional or monotonic response for every outlet.

### Two-deflector comparison with baseline

The two-deflector case is different from baseline, but the numerical change in this test is modest:

- Largest absolute outlet change: **0.805 pp / 6.440 CFM**, at R0C3 and R1C3.
- Maximum percentage changes from 15.917% to 15.909%.
- Minimum percentage changes from 9.083% to 8.572%.
- Spread increases from 6.834 pp to 7.336 pp.
- Uniformity index decreases from 0.571 to 0.539.

Without a reviewed materiality threshold tied to measurements or engineering acceptance criteria, this report cannot classify that difference as materially significant. It can only state that the output is measurably different and quantify its size.

## Review conclusion

The corrected solver completes all five cases, returns 800.000 CFM in each, and exposes mirrored row behavior for this symmetric test geometry. The most pronounced redistribution occurs in the single-deflector cases; the two-deflector result remains closer to baseline. These are observations of the experimental model only and are not claims about real HVAC performance.

## Behavior Fix 2 — Unit-complete outlet display

The following table adds CMH and velocity availability to the same corrected
results. The review geometry supplies 300 mm × 300 mm outlet dimensions, but no
reviewed `free_area_ratio`. Consequently, the solver preserves %, CFM, and CMH
while returning velocity as explicitly unavailable. Substituting a free-area
ratio of 1 would violate the no-guessed-default requirement.

| Outlet | Airflow % | Airflow CFM | Airflow CMH | Outlet velocity m/s |
|---|---:|---:|---:|---|
| **No deflector** |||||
| R0C0 | 9.083 % | 72.664 CFM | 123.457 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C1 | 15.917 % | 127.336 CFM | 216.345 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C2 | 15.917 % | 127.336 CFM | 216.345 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C3 | 9.083 % | 72.664 CFM | 123.457 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C0 | 9.083 % | 72.664 CFM | 123.457 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C1 | 15.917 % | 127.336 CFM | 216.345 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C2 | 15.917 % | 127.336 CFM | 216.345 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C3 | 9.083 % | 72.664 CFM | 123.457 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| **One deflector at 30°** |||||
| R0C0 | 7.117 % | 56.932 CFM | 96.728 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C1 | 12.471 % | 99.767 CFM | 169.505 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C2 | 12.471 % | 99.767 CFM | 169.505 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C3 | 17.942 % | 143.535 CFM | 243.867 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C0 | 7.117 % | 56.932 CFM | 96.728 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C1 | 12.471 % | 99.767 CFM | 169.505 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C2 | 12.471 % | 99.767 CFM | 169.505 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C3 | 17.942 % | 143.535 CFM | 243.867 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| **One deflector at 45°** |||||
| R0C0 | 7.477 % | 59.819 CFM | 101.633 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C1 | 13.103 % | 104.826 CFM | 178.100 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C2 | 18.020 % | 144.161 CFM | 244.930 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C3 | 11.399 % | 91.195 CFM | 154.941 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C0 | 7.477 % | 59.819 CFM | 101.633 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C1 | 13.103 % | 104.826 CFM | 178.100 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C2 | 18.020 % | 144.161 CFM | 244.930 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C3 | 11.399 % | 91.195 CFM | 154.941 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| **One deflector at 60°** |||||
| R0C0 | 7.948 % | 63.581 CFM | 108.025 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C1 | 14.211 % | 113.684 CFM | 193.151 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C2 | 17.872 % | 142.975 CFM | 242.916 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C3 | 9.970 % | 79.760 CFM | 135.512 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C0 | 7.948 % | 63.581 CFM | 108.025 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C1 | 14.211 % | 113.684 CFM | 193.151 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C2 | 17.872 % | 142.975 CFM | 242.916 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C3 | 9.970 % | 79.760 CFM | 135.512 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| **Two deflectors** |||||
| R0C0 | 8.572 % | 68.579 CFM | 116.517 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C1 | 15.909 % | 127.270 CFM | 216.232 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C2 | 15.631 % | 125.047 CFM | 212.457 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R0C3 | 9.888 % | 79.104 CFM | 134.398 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C0 | 8.572 % | 68.579 CFM | 116.517 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C1 | 15.909 % | 127.270 CFM | 216.232 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C2 | 15.631 % | 125.047 CFM | 212.457 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |
| R1C3 | 9.888 % | 79.104 CFM | 134.398 m³/h | unavailable — `OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE` |

For a valid-geometry display, the same result object exposes a numeric `m/s`
value only after the caller supplies a valid `free_area_ratio`; tests cover that
calculation without introducing a ratio into this engineering review fixture.
