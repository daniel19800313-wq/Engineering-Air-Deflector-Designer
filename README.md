# Air Deflector Designer (ADD)

Air Deflector Designer is an engineering design assistant for HVAC engineers who need to improve uneven airflow at multi-cell ceiling outlets. It helps engineers describe an outlet and air box, identify weak-air regions, compare deflector concepts, and save an auditable design decision before fabrication.

## Primary V1 field problem

The primary acceptance scenario is a ceiling outlet with eight cells arranged as a 2 × 4 grid. Air enters its plenum from a duct with strongly biased direction and momentum. In a typical field observation, roughly four cells deliver usable airflow while the other four are very weak.

In ADD, a **deflector** primarily means an internal airflow guide plate installed inside or immediately behind the multi-cell grille/plenum outlet region. The engineer needs to decide where to place this plate, how far to insert it into the dominant flow path, how wide it should be, and what angle it should use.

V1 must support this causal comparison:

```text
biased inlet flow
→ interaction with deflector
→ estimated intercepted relative airflow
→ estimated redirected relative airflow
→ redistribution across the eight outlet cells
```

The main product question is: given the inlet direction, plenum geometry, 2 × 4 outlet grid, and four observed weak cells, which deflector position, insertion length, width, and angle are most likely to improve relative airflow distribution without causing unacceptable loss in the previously strong cells?

## Product boundary

ADD V1 is **not CFD** and must not present its output as a computed physical velocity or pressure field. Its engine produces a fast, relative airflow-distribution estimate from simplified geometry, directional influence, obstruction, and tunable engineering coefficients. Animated particles and streamlines visualize that estimate; they are not measurement data.

Before the final estimator is implemented, its solver architecture, inputs, assumptions, equations, conservation method, pressure/resistance relationships, deflector interaction, downstream propagation, convergence, output schema, and validation limits must pass review. The controlling V0.1 specification is [docs/validation/SOLVER_SPEC_V0.1.md](docs/validation/SOLVER_SPEC_V0.1.md).

The V1 promise is:

- Rapid comparison of deflector alternatives.
- A consistent, explainable engineering workflow.
- Before/after relative distribution and balance indicators.
- Saved assumptions, geometry, engine version, and results.
- A path to calibration against field measurements and, later, CFD.

For the primary scenario, every baseline/candidate comparison must provide:

1. Baseline and candidate relative distributions for all eight cells.
2. Per-cell change in percentage points.
3. Weak-cell improvement and strong-cell reduction summaries.
4. Estimated intercepted-flow fraction, explicitly labeled as a model estimate.
5. Estimated redirected-flow allocation by outlet cell.
6. Warnings when geometry or model assumptions make the result unreliable.

## Architecture status

This repository is currently **conditionally approved** at the architecture review gate. D-01 through D-08 are approved in principle, but no production implementation should begin until the revised Sprint 1 exit checklist in [TASK.md](TASK.md) is accepted. The next approved activity is the isolated Sprint 1.5 estimator spike, not full Sprint 2 implementation.

## Proposed technology

- Web client: React, TypeScript, Three.js, Tailwind CSS.
- API: Python, FastAPI, Pydantic.
- Persistence: SQLite via SQLAlchemy and Alembic migrations.
- Calculation: a versioned, deterministic Python estimation engine behind a stable interface.
- Tests: Vitest and React Testing Library; pytest for API and engine; Playwright for critical workflows.

## Core workflow

1. Create or open a project.
2. Define units and design assumptions.
3. Build the outlet cell grid and plenum/air-box geometry; the primary V1 scenario is a 2 × 4 eight-cell grille.
4. Define inlet position, direction, and optional known flow.
5. Mark the observed weak cells; record any field measurements separately as validation evidence.
6. Add one or more parametric deflectors.
7. Run a deterministic estimate and inspect warnings.
8. Compare baseline and candidate distributions.
9. Save a design revision and export a fabrication-oriented summary in a later release.

Working edits are auto-saved as a mutable draft. A deliberate save/checkpoint creates a named Design revision. Running an estimate captures an immutable EstimationRun snapshot; auto-save must never create revision noise.

## Proposed repository layout

```text
air-deflector-designer/
├─ apps/
│  ├─ web/                    # React application
│  │  └─ src/
│  │     ├─ app/             # routing, providers, shell
│  │     ├─ features/        # projects, geometry, deflectors, compare
│  │     ├─ components/      # shared UI primitives
│  │     ├─ scene/           # Three.js scene and adapters
│  │     ├─ api/             # generated/typed API client
│  │     └─ state/           # editor/session state
│  └─ api/                    # FastAPI application
│     ├─ app/
│     │  ├─ api/             # HTTP routers and schemas
│     │  ├─ domain/          # entities and domain rules
│     │  ├─ services/        # use cases
│     │  ├─ simulation/      # estimation interfaces and V1 engine
│     │  ├─ persistence/     # SQLAlchemy repositories
│     │  └─ core/            # configuration, logging, errors
│     ├─ migrations/
│     └─ tests/
├─ packages/
│  ├─ contracts/             # OpenAPI-generated TypeScript types
│  └─ geometry/              # optional shared pure TS geometry helpers
├─ docs/
│  ├─ adr/                   # architecture decision records
│  ├─ validation/            # benchmark and calibration protocols
│  └─ ux/                    # workflow and wireframes
├─ TASK.md
├─ ARCHITECTURE.md
└─ README.md
```

This is a proposed structure, not yet scaffolded. A monorepo keeps the UI, API, contracts, and documentation versioned together without forcing a microservice architecture.

## Engineering principles

- Calculations are deterministic, versioned, unit-aware, and independently testable.
- Outlet cells are solved as a coupled sequential system: extracted upstream flow is deducted before downstream propagation.
- Mass, momentum, pressure/resistance, convergence, and residual handling belong to the solver—not the UI.
- Every displayed engineering value, heat map, comparison, ranking, gain/loss, or recommendation originates in versioned solver output.
- Absolute values are unavailable unless physical inputs, equations, calibration, and validated applicability support them.
- Domain objects do not depend on FastAPI, SQLAlchemy, React, or Three.js.
- Persist canonical parameters and results, not Three.js scene objects.
- Geometry editing is local and responsive; authoritative estimates run on the backend.
- Every result retains its input snapshot, engine version, warnings, and timestamp.
- UI language distinguishes **estimated**, **measured**, and, in future, **CFD-derived** values.
- Field notes and measurements remain separate, traceable engineering evidence and never overwrite a run.
- Reusable outlet templates are an architecture-reserved library for V1; designs always copy geometry into their own snapshot.

## Review questions

Sprint 1 should not close until the team agrees on:

1. Whether known inlet flow is required, optional, or unavailable in typical field work.
2. The first measured benchmark source and acceptable candidate-ordering criteria.
3. The minimum fabrication metadata required in V1 screens and exports.
4. Whether engineering notes and field validation need Sprint 2 CRUD or only schema/interface reservation.
5. The local data-directory convention and supported backup/restore user experience.
6. Target platforms and browsers for the local single-user release.

## Development rule

Please challenge my ideas whenever necessary. Do not simply agree with my design. If there is a better engineering approach, explain why and recommend it. Act like a senior software architect, not just a code generator.
