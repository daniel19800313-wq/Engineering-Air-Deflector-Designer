# ADD Solver Specification V0.1

Status: Pre-implementation architecture specification

This document defines the calculation boundary that must be reviewed before a final estimator is coded. It contains no fitted engineering constants and makes no claim of validated absolute-flow accuracy.

## 1. Solver architecture

The solver is a headless, deterministic domain component with no React, Three.js, HTTP, database, or animation dependency.

```text
SolverInput
  → input completeness and applicability validation
  → geometry preprocessing and ordered flow stations
  → initial state and boundary-condition construction
  → coupled pressure / resistance / mass-flow iteration
  → deflector momentum interaction
  → sequential cell extraction and downstream propagation
  → conservation and convergence audit
  → SolverOutput with provenance, residuals, warnings, and claim level
```

The production boundary is:

```text
solve(input_snapshot, solver_configuration) -> solver_output
```

Implementations sit behind this interface:

- `ConservationSkeleton`: enforces schemas, ordering, bookkeeping, residual reporting, and relative-only results; it contains no invented physical coefficients.
- `ReducedOrderSolver`: may calculate relative engineering estimates after Sprint 1.5 establishes defensible relationships and coefficients.
- Future validated absolute-flow or CFD adapter: may emit absolute values only inside its validated envelope.

The UI consumes solver output verbatim for all engineering displays. It may format units and presentation, but cannot calculate, interpolate, rank, recommend, clamp, or alter engineering values.

## 2. Required physical inputs

### Geometry

- Plenum width, height, depth, outlet location, and coordinate transform.
- Ordered 2 × 4 cell geometry: clear area, position, normal, and downstream sequence definition.
- Inlet location, dimensions/area, normal, and flow direction.
- Deflector position, insertion length, width, thickness, orientation, projected area relative to incident flow, and enabled state.
- Clearances and invalid intersections.

### Fluid and boundary conditions

Absolute-flow mode requires all inputs needed by the selected validated model, including:

- Air density or temperature, pressure, and humidity sufficient to derive it.
- Inlet boundary condition: measured total volume/mass flow, measured inlet velocity profile, or validated fan/duct pressure boundary.
- Outlet/static-pressure boundary condition.
- Cell/grille resistance relationship or validated loss coefficients, including its applicable Reynolds/geometry range.
- Wall and leakage assumptions.
- Deflector loss/redirection relationships and their applicable range.

If these are incomplete, the solver must reject absolute mode and may run only an explicitly supported relative mode.

### Observations and provenance

- Engineer-classified weak-cell set for comparison summaries.
- Optional measured field dataset, kept separate from solver predictions.
- Solver name/version, calibration profile/version, input units, and source metadata.

## 3. Assumptions and limitations

- V0.1 is a reduced-order control-volume/network model, not CFD and not a resolved velocity field.
- The primary geometry envelope is one rectangular plenum, one inlet, one 2 × 4 outlet, and zero or one planar rectangular internal guide plate.
- Flow is treated as steady for a run. Transients, acoustics, turbulence resolution, thermal buoyancy, leakage, compressibility, condensation, and flexible-plate deformation are excluded unless later modeled and validated.
- Each flow station has a representative bulk state; local recirculation and separation are represented only through validated reduced-order relationships.
- Outlet ordering must follow the calculated downstream path, not row/column index alone.
- Projected area is derived from geometry and incident direction by the solver, never entered or modified by the UI as an engineering result.
- No coefficient, resistance curve, redirection efficiency, or convergence tolerance receives a fabricated default. Missing required values produce an explicit validation error or relative-only eligibility result.

## 4. Calculation sequence

1. Validate geometry, units, boundary completeness, calibration applicability, and requested claim level.
2. Transform all geometry into canonical SI coordinates.
3. Determine incident direction and order outlet-cell extraction stations along the evolving bulk-flow path.
4. Build inlet mass/momentum state and pressure nodes.
5. Compute deflector projected area and interaction geometry from the current incident state.
6. Apply the selected validated deflector interaction relationship to partition incident flow into intercepted and residual components and redirect intercepted momentum.
7. Combine redirected and residual momentum into the downstream state using the declared reduced-order mixing rule.
8. At each ordered cell, solve its extraction flow from the current local pressure and cell resistance relationship.
9. Deduct extracted mass and momentum contribution before propagating to the next cell.
10. Update pressure losses/resistances, deflector interaction, cell extraction, and ordering where the model permits ordering changes.
11. Iterate until every required residual meets its configured, versioned criterion or the iteration limit is reached.
12. Audit mass balance, result applicability, and numerical validity; emit results only with claim level and warnings.

## 5. Mass-conservation method

For steady state, use control-volume bookkeeping. At station `k`:

```text
m_remaining[k+1] = m_remaining[k] - m_extracted[k] - m_leak[k]
```

For a sealed V0.1 plenum, leakage is zero only when explicitly assumed:

```text
R_mass = m_in - sum(m_cell[i]) - m_residual_exit - m_leak
```

The normalized residual is reported, not hidden:

```text
r_mass = abs(R_mass) / max(abs(m_in), mass_reference_floor)
```

The reference floor is a solver configuration item with documented units and rationale; it must not be silently invented. Relative mode uses a declared normalized inlet basis and labels all resulting quantities dimensionless/relative. It must not convert that basis to m³/s.

## 6. Pressure and resistance model

The intended network relationship for a cell or component is symbolic until a validated coefficient/curve is supplied:

```text
Δp_component = resistance_law(q, geometry, fluid_state, calibrated_parameters)
```

A commonly applicable quadratic form may be supported only when its assumptions and coefficient source are valid:

```text
Δp = K · (ρ v² / 2),       q = A · v
```

This equation does not authorize guessing `K`. Cell extraction is solved as a coupled pressure/resistance problem because extraction changes remaining flow and downstream pressure. The first production solver must not publish a pressure distribution or pressure-loss number until its resistance laws, boundary conditions, and calibration are defensible. The conservation skeleton may emit pressure nodes as `unavailable` with missing-input reasons.

## 7. Deflector interaction model

The solver derives projected area using deflector area `A_d`, incident unit direction `u`, and plate unit normal `n`:

```text
A_projected = A_d · abs(u · n)
```

Geometric overlap limits the portion of the incident stream that can interact with the plate. A selected, validated interaction model must then calculate:

```text
m_incident = m_intercepted + m_bypass
```

and a momentum balance of the form:

```text
F_plate + m_incident·V_incident
  = m_bypass·V_bypass + m_redirected·V_redirected + momentum_loss_terms
```

The redirection direction, intercepted fraction, loss terms, and any spreading/mixing law require either a defensible derivation or calibrated parameters. Geometry alone is insufficient. The solver reports incident direction, projected area, intercepted estimate, redirected estimate, bypass/residual estimate, parameter provenance, and applicability warnings.

## 8. Downstream propagation method

Outlet cells are not independent parallel score calculations. The solver maintains an ordered downstream state containing remaining mass basis, bulk momentum vector, representative pressure, and accumulated losses.

For each cell in solver-determined order:

1. Solve extraction from the current pressure/resistance state.
2. Limit extraction so it cannot exceed available remaining mass basis.
3. Deduct extracted flow from the downstream mass balance.
4. Deduct or update momentum according to the declared outlet extraction model.
5. Apply segment losses and propagate the updated pressure and direction.
6. Record the complete before/extracted/after state for audit.

If recirculation or multiple competing paths cannot be represented reliably by a single ordering, the solver must warn/out-of-envelope rather than force a plausible-looking sequence.

## 9. Iterative convergence criteria

Each solver version/configuration must explicitly provide dimensioned or normalized tolerances, maximum iterations, and relaxation method. The required convergence checks are:

- normalized global mass residual;
- maximum pressure-node update residual when pressure is solved;
- maximum cell-flow update residual;
- maximum momentum-vector update residual;
- stable active constraints and downstream ordering where applicable.

Symbolically, convergence requires all enabled checks:

```text
r_mass ≤ ε_mass
r_pressure ≤ ε_pressure
r_cell_flow ≤ ε_cell_flow
r_momentum ≤ ε_momentum
```

No numerical epsilon is specified before the solver formulation, numeric scale, and validation cases exist. Reaching `max_iterations` without satisfying every enabled criterion returns `not_converged`; the UI must not promote that result into recommendations.

## 10. Solver output schema

```text
SolverOutput
  run_id
  solver_name
  solver_version
  calibration_profile
  claim_level: relative_estimate | validated_absolute
  validation_state
  convergence:
    status
    iterations
    configured_tolerances
    mass_residual
    pressure_residual
    cell_flow_residual
    momentum_residual
  applicability:
    inside_validated_envelope
    missing_inputs[]
    assumptions[]
    warnings[]
  deflector:
    incident_direction
    projected_area_m2
    intercepted_fraction_estimate
    redirected_fraction_estimate
    residual_fraction_estimate
    momentum_direction_after
    pressure_loss_pa | unavailable
  cells[]:
    row_index
    column_index
    downstream_order
    incoming_relative_or_mass_flow
    extracted_relative_share
    extracted_flow_m3_s | unavailable
    outgoing_relative_or_mass_flow
    local_pressure_pa | unavailable
    redirected_allocation_pct
  comparison:
    baseline_run_id
    cell_delta_percentage_points[]
    weak_cell_improvement
    strong_cell_reduction
    ranking | unavailable
    recommendation | unavailable
```

Rankings and recommendations must be solver outputs derived under an approved objective/constraint definition. The UI cannot calculate them. Unavailable fields remain explicitly unavailable rather than zero or omitted ambiguously.

## 11. Validation and calibration plan

1. Verify bookkeeping with synthetic conservation cases and known algebraic network cases.
2. Test determinism, symmetry, ordering, non-negativity, extraction bounds, and residual reporting.
3. Compare parcel/ray and influence/network prototypes using the shared primary 2 × 4 cases.
4. Acquire measured baseline and multiple deflector candidates with geometry, inlet conditions, per-cell measurements, instrumentation, and uncertainty.
5. Separate calibration and holdout cases. Never assess accuracy only on fitted cases.
6. Evaluate candidate ordering, per-cell distribution error, weak/strong trade-off, conservation residuals, sensitivity, and runtime.
7. Define a supported geometry/flow/Reynolds/calibration envelope and reject or downgrade results outside it.
8. Version every equation set, coefficient source, calibration dataset, and acceptance threshold.
9. Permit `validated_absolute` only after independent engineering review accepts boundary completeness and absolute-flow/pressure error limits.

## 12. Claims not yet permitted

Until validated evidence exists, ADD cannot claim:

- physically precise absolute cell flow, velocity, static pressure, or pressure loss;
- resolved turbulence, separation, recirculation, or streamline fidelity;
- physically precise intercepted or redirected mass-flow fractions;
- universal material/surface effects;
- global optimality of a deflector;
- performance outside the documented geometry and calibration envelope;
- compliance, safety, fabrication fitness, or replacement for field measurement/CFD.

V0.1 may claim only deterministic, conservation-audited **relative engineering estimates** inside the documented model envelope, with explicit residuals, assumptions, solver provenance, and validation state.
