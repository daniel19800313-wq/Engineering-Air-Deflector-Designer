# ADD V0.1 HVAC Domain Review Package

Status: Engineering validation required before solver implementation

Purpose: obtain HVAC-domain approval or correction of the reduced-order solver formulation. This package contains no coefficient values and does not authorize absolute-flow or pressure claims.

## Classification legend

| Classification | Meaning |
|---|---|
| Established physical relationship | Conservation or standard physical definition; its application and boundary still require review |
| Engineering approximation | Reduced-order representation that omits resolved flow behavior and requires an applicability envelope |
| Calibration-dependent relationship | Equation form or coefficient must be supported by manufacturer data, experiment, literature, or project calibration |
| Placeholder not yet permitted | Conceptual slot only; it cannot produce a displayed engineering value until replaced by an approved relationship |

## 1. Control volumes and state definitions

Proposed control volumes:

1. **Inlet control surface:** duct-to-plenum entry, with area, bulk velocity/mass flow, pressure boundary, and incident momentum direction.
2. **Deflector interaction volume:** the incident stream region geometrically overlapping the internal guide plate.
3. **Sequential plenum segments:** ordered volumes between extraction events, each carrying remaining mass basis, bulk momentum direction, representative pressure, and accumulated loss.
4. **Outlet-cell control surfaces:** eight extraction surfaces, each with clear area, normal, local pressure, resistance relationship, and extracted flow.
5. **Residual outlet/control surface:** any mass remaining after the final modeled cell, if the selected domain permits such an exit.

The proposed segment state before cell `k` is:

```text
S_k = {m_remaining,k, M_k, p_k, ρ_k, loss_state_k}
```

| Item | Classification | Engineering review required |
|---|---|---|
| Control-volume mass and momentum balance | Established physical relationship | Confirm boundaries and included fluxes/forces |
| One representative bulk state per segment | Engineering approximation | Confirm when mixing, recirculation, or separation makes it invalid |
| Single sequential extraction path | Engineering approximation | Confirm how outlet order is determined and when multiple paths invalidate it |
| Residual exit after final cell | Placeholder not yet permitted | Confirm whether the physical enclosure has any modeled residual outlet/leak path |

## 2. Symbolic conservation equations

### Steady mass balance

For each sequential segment:

```text
m_remaining,k+1 = m_remaining,k - m_cell,k - m_leak,k
```

Global balance:

```text
R_mass = m_in - Σ m_cell,i - m_residual_exit - m_leak
```

Classification: **established physical relationship**.

Review questions: Is leakage excluded, measured, or modeled? Is there a residual exit? Are density changes negligible for the expected operating range?

### Steady linear momentum balance

For a control volume:

```text
ΣF_external = Σ_out(m · V) - Σ_in(m · V)
```

Expanded forces may include pressure forces, wall/deflector reaction, and modeled losses.

Classification: **established physical relationship**. Reducing the real three-dimensional field to bulk vectors is an **engineering approximation**.

### Relative-only mass basis

When absolute boundary data/model validation is unavailable:

```text
m*_in = 1
m*_remaining,k+1 = m*_remaining,k - m*_cell,k - m*_leak,k
Σm*_out = 1 within residual tolerance
```

Classification: **engineering approximation**. It provides dimensionless relative allocation only and cannot be converted to kg/s or m³/s.

## 3. Deflector interception and momentum redirection

### Plate projected area

For plate area `A_d`, incident unit direction `u`, and plate unit normal `n`:

```text
A_projected = A_d · |u · n|
```

Classification: **established geometric relationship** for projection of a planar area. It does not by itself determine intercepted flow.

### Geometric overlap

```text
A_effective = overlap(projected incident stream region, projected deflector region)
```

Classification: **engineering approximation** because the “incident stream region” is a reduced-order construct rather than a resolved velocity profile.

### Intercepted fraction

Candidate relationship:

```text
f_intercept = F_intercept(
  A_effective / A_incident,
  incidence_angle,
  blockage,
  Reynolds_number,
  geometry_parameters,
  calibrated_coefficients
)

m_intercepted = f_intercept · m_incident
m_bypass = m_incident - m_intercepted
```

Classification: `F_intercept` is a **calibration-dependent relationship**. Area ratio alone as the interception fraction is a **placeholder not yet permitted**.

### Momentum redirection

```text
F_plate + m_incident V_incident
  = m_bypass V_bypass
  + m_redirected V_redirected
  + momentum_loss_terms
```

Classification: momentum balance is an **established physical relationship**. The following are **calibration-dependent relationships**: redirection efficiency, outgoing angle, bypass direction, spreading/mixing, separation loss, and momentum-loss terms.

No specular-reflection rule, fixed turn angle, or fixed redirection efficiency is currently permitted without engineering evidence.

## 4. Outlet resistance and pressure-flow relationships

General component relationship:

```text
Δp_cell = R_cell(q_cell, ρ, μ, geometry, product_data, calibrated_parameters)
```

Classification: `R_cell` is a **calibration-dependent relationship**.

A quadratic loss form may be considered:

```text
Δp = K · ρv²/2
q = A · v
```

| Term/equation | Classification | Review condition |
|---|---|---|
| `q = A·v` for a defined mean normal velocity | Established physical relationship | Confirm effective/clear area definition |
| Dynamic pressure `ρv²/2` | Established physical relationship | Confirm incompressible operating range |
| Quadratic component loss `Δp = Kρv²/2` | Calibration-dependent relationship | Requires valid `K`, reference area/velocity, direction, Reynolds and geometry range |
| Same `K` for all cells | Placeholder not yet permitted | Cell geometry/orientation/product evidence required |
| Generic grille resistance without manufacturer/test data | Placeholder not yet permitted | Cannot produce pressure or absolute extraction |

Proposed cell extraction coupling:

```text
p_plenum,k - p_outlet,k = R_cell(q_cell,k, ...)
```

Classification: pressure balance is an **established physical relationship**; using one representative `p_plenum,k` per segment is an **engineering approximation**; `R_cell` is **calibration-dependent**.

## 5. Pressure distribution

Proposed segment update:

```text
p_k+1 = p_k - Δp_segment,k - Δp_interaction,k
```

Classification: pressure accounting is an **established physical relationship**. The segment and interaction loss functions are **calibration-dependent relationships**.

Pressure redistribution in a real plenum may be multidimensional. A one-dimensional ordered pressure chain is an **engineering approximation** and must be rejected when recirculation or competing paths dominate.

Until resistance laws, pressure boundaries, fluid state, and validation are available, numerical `p_k`, `Δp_cell`, and `Δp_deflector` outputs are **placeholders not yet permitted** and must remain `unavailable`.

## 6. Downstream state propagation

After extraction at cell `k`:

```text
m_remaining,k+1 = m_remaining,k - m_cell,k
```

Classification: **established physical relationship**.

Proposed bulk momentum update:

```text
M_k+1 = M_k - M_extracted,k + J_redirect,k - J_loss,k
V_bulk,k+1 = M_k+1 / m_remaining,k+1
```

Classification: conservation structure is an **established physical relationship**. Models for extracted momentum, redirected impulse, mixing, wall force, and loss impulse are **calibration-dependent relationships**. Representing the result as one bulk direction is an **engineering approximation**.

The next outlet cell must be evaluated from `S_k+1`; it cannot reuse the inlet state or an unchanged total-flow value.

Proposed ordering rule:

```text
order = G(cell_positions, evolving_bulk_direction, geometry)
```

Classification: `G` is an **engineering approximation** requiring explicit definition and tests. Dynamically changing order during iteration may be numerically discontinuous and requires domain review.

## 7. Convergence and residual definitions

### Mass residual

```text
r_mass = |m_in - Σm_out| / max(|m_in|, m_reference_floor)
```

Classification: normalized conservation residual is an **established numerical relationship**. `m_reference_floor` is **calibration/configuration-dependent** and cannot receive a guessed value.

### Pressure update residual

```text
r_pressure = max_k |p_k^(n+1) - p_k^n| / p_reference
```

Classification: **engineering numerical approximation**. Norm, scaling, and tolerance require solver/numerical review.

### Cell-flow update residual

```text
r_cell = max_i |q_i^(n+1) - q_i^n| / q_reference
```

Classification: **engineering numerical approximation**. Reference and tolerance are not yet approved.

### Momentum update residual

```text
r_momentum = ||M^(n+1) - M^n|| / M_reference
```

Classification: **engineering numerical approximation**. Norm, reference, and tolerance are not yet approved.

Required convergence decision:

```text
converged =
  r_mass ≤ ε_mass
  and r_pressure ≤ ε_pressure   [when pressure is solved]
  and r_cell ≤ ε_cell
  and r_momentum ≤ ε_momentum
  and active constraints/order are stable
```

Classification: multi-residual convergence structure is an **engineering numerical approximation**. All epsilon values, maximum iterations, relaxation, stability window, and divergence rules are **placeholder not yet permitted** until reviewed. Non-converged output cannot be ranked or recommended.

## 8. Required physical-input review table

No site documents were supplied with this review package. Therefore “currently available” is recorded as unknown rather than inferred.

| Input name | Unit | Mandatory | Expected source | Currently available from site documents | Consequence if missing |
|---|---:|---|---|---|---|
| Plenum internal width/height/depth | m | Yes | Site drawing, survey, fabrication drawing | Unknown — not provided for review | Cannot establish geometry envelope or control volumes |
| Outlet location/orientation in plenum | m, degrees/vector | Yes | Drawing or site measurement | Unknown — not provided for review | Cannot order extraction or transform cell geometry |
| Cell rows/columns and clear dimensions | count, m | Yes | Manufacturer submittal or measurement | Unknown — not provided for review | Cannot calculate areas or eight-cell allocation |
| Cell clear/effective area | m² | Yes for pressure/absolute mode | Manufacturer data or measured geometry | Unknown — not provided for review | Pressure-flow extraction unavailable; relative model may also be invalid |
| Cell normal/orientation | unit vector/degrees | Yes | Product geometry or survey | Unknown — not provided for review | Outlet momentum and extraction direction unavailable |
| Inlet location and dimensions | m | Yes | Duct/plenum drawing or survey | Unknown — not provided for review | Incident region and direction cannot be established |
| Inlet airflow direction/profile | unit vector plus profile | Yes | Traverse measurement, duct geometry, validated assumption | Unknown — not provided for review | Primary biased-flow condition cannot be represented defensibly |
| Total inlet volume or mass flow | m³/s or kg/s | Required for absolute mode | TAB report or calibrated instrument measurement | Unknown — not provided for review | Absolute flow unavailable; relative mode only if otherwise supported |
| Inlet static/total pressure boundary | Pa | Required for pressure-driven absolute mode | TAB report, sensor, fan/duct model | Unknown — not provided for review | Pressure-driven solution unavailable |
| Outlet/room static pressure boundary | Pa | Required for pressure solution | Measurement or justified reference condition | Unknown — not provided for review | Pressure differences and extraction unavailable |
| Air temperature | °C or K | Required to derive density for absolute mode | Site measurement/BMS/TAB | Unknown — not provided for review | Density-dependent absolute pressure/momentum calculations unavailable |
| Barometric/absolute pressure | Pa | Conditional for density | Site measurement or weather-calibrated source | Unknown — not provided for review | Density uncertainty; absolute claims may be unavailable |
| Relative humidity | %RH | Conditional for required density accuracy | Site measurement/BMS/TAB | Unknown — not provided for review | Density uncertainty must be assessed, not defaulted silently |
| Air density | kg/m³ | Required for absolute momentum/pressure | Derived from approved state inputs or measured | Unknown — not provided for review | Absolute momentum/dynamic-pressure relationships unavailable |
| Dynamic viscosity | Pa·s | Required when Reynolds applicability matters | Derived from air state using approved source | Unknown — not provided for review | Reynolds-dependent resistance applicability cannot be checked |
| Deflector position | m | Yes | Proposed design/site measurement | Unknown — not provided for review | Interaction geometry cannot be solved |
| Deflector insertion length | m | Yes | Proposed design/fabrication drawing | Unknown — not provided for review | Effective overlap cannot be solved |
| Deflector width/thickness | m | Yes | Proposed design/fabrication drawing | Unknown — not provided for review | Plate area, blockage, and clearances unavailable |
| Deflector orientation/normal | degrees/unit vector | Yes | Proposed design/site measurement | Unknown — not provided for review | Projected area and redirection unavailable |
| Grille/cell resistance curve or loss coefficient | Pa vs m³/s, or dimensionless K | Required for pressure/absolute mode | Manufacturer test data or controlled testing | Unknown — not provided for review | Pressure and absolute sequential extraction unavailable |
| Deflector interaction/loss data | model-specific | Required for validated redirection | Controlled experiment, literature, calibrated dataset | Unknown — not provided for review | Precise interception/redirection unavailable; no guessed efficiency allowed |
| Leakage path/flow | m², kg/s, or relationship | Conditional | Leakage test, fabrication specification | Unknown — not provided for review | Must explicitly exclude absolute claims or quantify mass-balance uncertainty |
| Weak-cell classification | cell IDs | Yes for weak/strong summaries | Engineer field observation | Unknown — not provided for review | Solver may produce distribution but not weak-cell improvement summary |
| Baseline per-cell measurements | m/s, m³/s, or approved relative measure | Required for calibration/validation | TAB/field measurement | Unknown — not provided for review | Candidate agreement and calibration cannot be established |
| Candidate per-cell measurements | same as baseline | Required to validate candidate ordering | Controlled field tests | Unknown — not provided for review | Deflector-effect accuracy and ordering cannot be validated |
| Instrument model and accuracy | model, ± unit/% | Required for validation | Calibration certificate/test record | Unknown — not provided for review | Measurement uncertainty and acceptance thresholds cannot be defended |
| Fan operating condition | Hz, rpm, control %, static pressure | Required to compare field cases | BMS/VFD/TAB record | Unknown — not provided for review | Baseline/candidate measurements may not be comparable |

## 9. Calibration coefficients requiring approval

No value is proposed for any coefficient.

| Coefficient/relationship | Classification | Required evidence |
|---|---|---|
| Cell/grille resistance curve or `K_cell` | Calibration-dependent relationship | Manufacturer test or controlled flow/pressure testing with reference-area convention |
| Deflector interception function parameters | Calibration-dependent relationship | Measured interception/redistribution cases over position, insertion, width, and angle |
| Redirection efficiency and outgoing-angle relationship | Calibration-dependent relationship | Momentum/flow measurements or defensible validated source |
| Deflector pressure-loss coefficient | Calibration-dependent relationship | Pressure measurements across applicable geometries and flow range |
| Mixing/spreading parameters | Calibration-dependent relationship | Per-cell distributions across holdout configurations |
| Segment/wall loss coefficients | Calibration-dependent relationship | Geometry-specific evidence or validated reduced-order source |
| Extracted-momentum model parameters | Calibration-dependent relationship | Outlet velocity direction/profile evidence |
| Relaxation factors | Engineering numerical approximation | Numerical stability study; not a physical calibration coefficient |
| Residual tolerances and reference floors | Engineering numerical approximation | Scale analysis, benchmark closure, sensitivity, and validation requirements |
| Any universal fixed efficiency or default `K` | Placeholder not yet permitted | Must not exist without the evidence above |

Calibration must separate fitting cases from holdout validation cases and record equation version, coefficient source, uncertainty, geometry/flow envelope, instrument provenance, and applicability checks.

## 10. Unsupported claims and validation boundaries

Not currently permitted:

- absolute airflow per cell;
- absolute plenum/cell pressure or deflector pressure loss;
- physically precise intercepted, redirected, or residual mass fractions;
- resolved velocity fields, turbulence, recirculation, separation, or physical streamlines;
- universal outlet or deflector coefficients;
- material/surface effects without validated relationships;
- reliable behavior with multiple flow paths, strong recirculation, leakage, multiple inlets, multiple deflectors, or geometry outside the V0.1 envelope;
- globally optimal deflector designs;
- rankings or recommendations from non-converged or outside-envelope results;
- compliance, safety, fabrication fitness, or replacement for CFD/TAB/site testing.

Potential claim after the conservation skeleton and relative model are reviewed and validated:

> Deterministic, conservation-audited relative engineering estimates for comparative deflector candidates within the documented 2 × 4 geometry and calibration envelope.

Potential absolute-flow claims require a separate approval based on complete physical inputs, accepted equations/coefficient provenance, convergence evidence, uncertainty analysis, calibration/holdout performance, and explicit error limits.

## Engineering reviewer decisions

For each item, record **approve**, **revise**, **reject**, or **insufficient evidence**:

1. Control-volume boundaries and leakage/residual-exit treatment.
2. Applicability of a single sequential bulk-flow path.
3. Outlet ordering and whether it may change during iteration.
4. Valid pressure/resistance relationship and reference area for the outlet product.
5. Deflector interception, redirection, mixing, and loss relationships.
6. Required air-state and boundary-condition measurements.
7. Momentum removal model at each outlet cell.
8. Residual norms, scaling, tolerances, relaxation, and iteration limits.
9. Minimum calibration and independent validation dataset.
10. Relative and absolute claim envelopes and acceptable errors.
