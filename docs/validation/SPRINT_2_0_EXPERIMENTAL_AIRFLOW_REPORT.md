# Sprint 2.0 Experimental Airflow Solver Report

Status: Complete — prototype awaiting review and calibration

## Implemented model

The first executable eight-outlet prototype combines a replaceable directional area/distance distribution kernel, a replaceable projected-area/geometric-reflection deflector influence model, normalized shares, supplied-total CFM scaling, and the approved sequential conservation evaluator.

The model supports one rectangular plenum, one explicitly directed inlet, exactly eight ordered rectangular outlets, and one or more rectangular deflectors rotated about global +Y. Every output carries experimental-model provenance and the claim label `experimental_scaled_distribution`.

## Engineering and mathematical facts used

- Canonical coordinate transforms and explicit unit-vector validation.
- Rectangle area, dot products, distance, planar projection, and geometric reflection.
- Non-negative weight normalization.
- Explicit supplied-total scaling and sequential conservation accounting.

## Experimental assumptions used

- Outlet influence is proportional to clear area and positive directional alignment and inversely proportional to squared distance.
- Intercepted fraction proxy is projected deflector area divided by inlet area, bounded to the valid fraction interval.
- Redirected direction proxy is geometric reflection about the deflector normal.
- Current and redirected weights mix using the interception proxy.
- Multiple deflectors apply sequentially in supplied order.
- Normalized shares scaled by supplied inlet CFM are experimental outlet estimates.

They were chosen because they are transparent, deterministic, coefficient-free, sensitive to the required geometry/angle/position inputs, modular, and calibratable. They are not asserted to be validated HVAC physics.

## Verification and goldens

Six deterministic prototype goldens cover positive/negative angle, zero projected influence, position shift, multiple deflectors, and invalid inlet direction. Tests prove eight outputs, supplied-total conservation, deterministic behavior, deflector angle/position sensitivity, multiple-deflector support, failure isolation, experimental claim/provenance, and corrupted-golden detection.

All earlier framework, geometry interaction, and sequential extraction tests and runners remain passing.

## Limitations

- No pressure, resistance, grille behavior, momentum magnitude, turbulence, recirculation, wall interaction, wake, separation, leakage, density, fan curve, or thermal effect.
- Geometric reflection is not aerodynamic redirection.
- Projected-area ratio is not a validated interception relationship.
- Distance/alignment weights are not a validated outlet-flow relationship.
- Deflector ordering is not a coupled multi-body solution.
- Estimated outlet CFM is scaled allocation of supplied total, not validated absolute measurement.
- Center-in-domain validation is not full solid containment or collision detection.

## Future improvements

- Calibrate formula structure/parameters against measured baseline and candidate AHU cases.
- Replace distribution and deflector modules independently with reviewed models.
- Add outlet resistance and pressure only after physical inputs/equations are reviewed.
- Introduce leakage, density, uncertainty, and validation envelopes when supported by evidence.
- Compare candidate ordering against holdout measurements and verified CFD where appropriate.

## Review statement

**Sprint 2.0 produces an experimental, deterministic, conservation-audited airflow-distribution prototype. It has not been validated for HVAC design, fabrication, performance, pressure, or absolute outlet airflow accuracy. Stop after this sprint and await review.**
