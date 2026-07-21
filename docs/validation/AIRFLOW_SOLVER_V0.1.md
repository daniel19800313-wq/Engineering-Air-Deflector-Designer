# ADD Experimental Airflow Solver V0.1

Status: Prototype model specification — not validated HVAC physics

## Purpose

Produce the first deterministic, executable eight-outlet distribution estimate for discussion and later calibration. The model is deliberately simple and replaceable. Its output is labelled `experimental_scaled_distribution`; it is not a validated absolute airflow prediction.

## Minimum input conventions

### Coordinate system

Use the approved right-handed SI geometry frame: X left-to-right across the outlet, Y bottom-to-top, and Z from outlet into plenum. Positions and dimensions are metres. Airflow input/output is CFM because Sprint 2.0 explicitly supplies total CFM; internal distribution shares are dimensionless.

The rectangular plenum occupies X from negative half-length to positive half-length, Y from negative half-width to positive half-width, and Z from zero at the outlet plane to the supplied height. V0.1 validates component centers against this domain.

### Inlet airflow direction

The caller supplies an explicit finite unit vector pointing from the inlet into the plenum. Position alone never determines direction. The solver rejects missing, zero, non-unit, or non-finite directions and does not normalize them automatically.

### Deflector rotation axis

V0.1 supports rotation about the global positive Y axis only. No other axis is inferred. Each deflector has explicit center, width along global X, height along its local in-plane axis, angle, and input order.

### Deflector angle convention

Angle is in degrees using the right-hand rule about +Y. At zero degrees the deflector surface normal points +Z. Positive rotation transforms the normal toward +X. Angles must be finite; equivalent wrapped angles are accepted as supplied without rewriting stored input.

## Engineering and mathematical facts

- Rectangle area is width multiplied by height.
- Directional alignment is the vector dot product of unit directions.
- Planar projected area uses absolute normal/direction alignment.
- Geometric reflection about a plane normal is deterministic vector geometry.
- Normalized non-negative weights sum to one.
- Multiplying normalized shares by explicitly supplied total CFM preserves that supplied total within the explicit conservation comparison policy.
- Sequential downstream accounting subtracts each accepted outlet estimate from the previous remaining amount.

These facts do not establish that the selected proxies reproduce real plenum flow.

## Experimental assumptions

### Baseline distribution proxy

For each outlet, construct the vector from inlet center to outlet center. Its unnormalized influence is:

```text
outlet clear area × positive inlet-direction alignment ÷ squared distance
```

Negative/backward alignment contributes no weight. If all outlets have zero weight, the case is rejected rather than repaired.

This resembles a directional geometric spreading proxy. It is not a pressure, resistance, momentum, turbulence, or grille model.

### Deflector interception proxy

For each deflector in explicit input order, calculate plate projected area relative to inlet direction. The experimental intercepted fraction is projected plate area divided by inlet area, bounded to the physically meaningful interval from none to all.

This area ratio is an authorized prototype assumption for this sprint only. It was previously prohibited as a validated relationship and remains unvalidated.

### Deflector redirection proxy

Reflect the current inlet direction geometrically about the deflector normal. Calculate outlet weights from the deflector center using the same area/alignment/distance proxy. Mix current weights and redirected weights using the experimental intercepted fraction.

Geometric reflection is not a claim that air reflects specularly. Plate position affects distances/alignment; angle affects projected area and reflected direction; width/height affect projected area.

### Multiple deflectors

Apply deflectors sequentially in their supplied order. This is a deterministic prototype composition rule, not a multiple-body aerodynamic interaction model.

### Outlet CFM

Normalize final weights to shares and scale them by the explicitly supplied inlet total CFM. Values are experimental allocations constrained to conserve the supplied total; they are not validated absolute outlet measurements.

To prevent floating-point accumulation from creating forbidden over-extraction, the solver derives each extraction from the difference between the previously accepted remaining total and the next cumulative-share remaining target; the final target is explicitly zero. This is numerical closure of the normalized allocation, not an aerodynamic assumption or residual tolerance.

## Inputs

- Rectangular plenum length, width, height.
- Inlet center, width, height, explicit unit direction, and positive finite total CFM.
- Exactly eight rectangular outlets with unique IDs, centers, positive width/height, and explicit downstream order.
- One or more planar rectangular deflectors with unique IDs, centers, angle about +Y, width, and height.
- Explicit conservation unit, comparison tolerance, tolerance provenance, and solver version.

Geometry must lie within the rectangular plenum bounds under the canonical coordinate convention. V0.1 validates centers and positive dimensions but does not perform full solid containment/collision modeling.

## Outputs

- Per outlet: ID, downstream order, experimental airflow percentage (`%`),
  unchanged experimental airflow (`CFM`), converted airflow (`m^3/h`), and
  outlet velocity (`m/s`) when explicit velocity geometry is valid.
- Velocity geometry is supplied separately as `width_mm`, `height_mm`, and
  `free_area_ratio`. Missing or invalid velocity geometry leaves velocity
  explicitly unavailable and does not alter percentage, CFM, or CMH.
- Outlet calculation provenance records total inlet CFM, the explicit
  `1.69901082 m^3/h per CFM` conversion, geometric area, supplied free-area
  ratio, effective area, the CMH-to-m^3/s conversion, and final velocity.
- Global: supplied total CFM, sum of estimated outlet CFM, terminal remaining CFM, conservation residual/status, validation label, assumptions, warnings, and solver version.
- Deflector audit: normal, projected area, experimental intercepted fraction, and whether redirected weights were usable.

Every engineering value originates in solver output. No UI calculation is authorized.

## Failure conditions

Reject invalid/non-finite geometry, non-unit inlet direction, non-positive airflow/areas, duplicate IDs/order, zero distance, all-zero baseline weights, a deflector whose redirected proxy has no usable outlet weights, unavailable provenance/policy, sequential accounting failure, or conservation failure. No defaults, coefficient guessing, input repair, or fallback equal distribution is permitted.

## Applicability and limitations

- One rectangular plenum, one inlet, exactly eight rectangular outlets, one or more rectangular deflectors.
- No outlet resistance, pressure, fan curve, grille behavior, leakage, density,
  predicted internal flow-field velocity, turbulence, recirculation, wall loss,
  thermal effect, or CFD. Reported outlet velocity is only the arithmetic bulk
  velocity derived from solver airflow and explicitly supplied effective area;
  it is not a validated local velocity prediction.
- Outlet normals and product characteristics are not modeled.
- Deflector obstruction, wake, attachment, separation, and loss are not modeled.
- Results are sensitive to the transparent proxy and cannot support fabrication, compliance, safety, or engineering-use confidence.
- Calibration against measured AHU baseline/candidate cases is required before model promotion.

## Replaceability

The orchestration depends on replaceable `DistributionKernel` and `DeflectorInfluenceModel` interfaces. Future calibrated or physical models may replace either without changing input validation, conservation accounting, result packaging, verification, or visualization boundaries.
