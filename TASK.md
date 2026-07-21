# ADD Delivery Plan

## Sprint 2.1 — Simulation Workspace UI Foundation

- [x] Add the first React/TypeScript simulation workspace under `apps/web`.
- [x] Add explicit inlet, grille/plenum, eight-cell grid, free-area, and multi-deflector editing.
- [x] Add the 2D schematic, solver-result matrix, heat map, summary, and outlet provenance detail.
- [x] Add the FastAPI `/api/v1/simulations/airflow` adapter to the existing solver.
- [x] Preserve missing free area and unavailable velocity without UI substitution.
- [x] Add frontend interaction and API contract tests.
- [x] Verify the production build, backend tests, and canonical airflow goldens.
- [x] Document the workspace in `docs/ui/SIMULATION_WORKSPACE_V0.1.md`.

Status: complete; awaiting Engineering UI Review 1. No solver allocation mathematics or golden datasets were changed.

### Engineering UI Review Fix 1

- [x] Remove UI-only `free_area_percent` from the strict API request payload.
- [x] Preserve canonical `free_area_ratio` from frontend type through solver adapter.
- [x] Replace mixed perspective with Outlet Face View and Side Section View.
- [x] Add complete `zh-TW` and `en` localization with persisted selection.
- [x] Replace raw backend errors with localized messages and expandable diagnostics.
- [x] Add bilingual, geometry-switching, request-contract, and error tests.

Status: implementation and verification complete; awaiting engineering review approval. Frontend tests, strict TypeScript compilation, production build, backend regression tests, canonical golden comparisons, and live browser workflow all passed.

### Sprint 2.2 — Engineering 3D Visualization Foundation

- [x] Replace the 2D preview with a true Three.js / React Three Fiber scene.
- [x] Render inlet, plenum, grille/outlet grid, and zero-to-many physical deflector plates in solver coordinates.
- [x] Add orbit rotate/pan/zoom and isometric, front, side, and top quick views.
- [x] Update scene geometry immediately without invoking the solver.
- [x] Render result-only outlet heat maps for %, CFM, CMH, and velocity.
- [x] Add result-driven engineering particle indicators without fluid simulation claims.
- [x] Add optional annotations and explicit non-CFD boundaries in both languages.
- [x] Add isolated geometry/result projection and interaction tests.

Status: implementation and verification complete; awaiting Engineering 3D Review. Frontend tests, strict TypeScript compilation, production build, backend regression tests, canonical airflow goldens, WebGL rendering, geometry-only editing, quick camera views, multi-deflector rendering, and result-driven overlays all passed. Solver mathematics, API contract, allocation logic, and canonical golden datasets remain unchanged.

### Sprint 2.2.1 — Configurable Inlet Airflow Direction

- [x] Add explicit inlet position and canonical X/Y/Z direction inputs.
- [x] Add six directional presets plus editable custom vector.
- [x] Reject zero-length/non-finite vectors and normalize valid directions.
- [x] Forward the identical normalized position and direction through FastAPI to the existing solver.
- [x] Add an explicit solver `(X,Y,Z)` to Three.js `(X,Z,Y)` presentation adapter.
- [x] Drive the inlet marker, arrow, and particle initial tangent from the canonical boundary.
- [x] Hide stale result heat maps and particles after any input edit.
- [x] Verify all six axial directions and a custom diagonal at contract and visualization boundaries.

Status: implementation and verification complete; awaiting Engineering UI Review. Frontend tests, strict TypeScript compilation, production build, 71 backend tests, nine canonical airflow goldens, live WebGL direction updates, normalized custom vectors, successful downward solver execution, and stale-result invalidation all passed. The solver may explicitly reject outward-pointing configurations with no positive outlet weights; the UI never fabricates an allocation.

### Sprint 2.2.2 — Real Fan Integration & Solver-driven Particle Visualization

- [x] Add governed SF-501 and SF-502 profiles with verified equipment identifiers and nameplate data.
- [x] Add independent enable, OFF/50/60/custom frequency, status, airflow, and pressure controls.
- [x] Calculate fan airflow and static pressure in the backend using only the approved affinity laws.
- [x] Sum fan airflow, convert it to CFM, and pass only the total to the unchanged Experimental Solver.
- [x] Return fan estimates, inlet velocity, labels, and provenance from the backend.
- [x] Create independent result-backed emitters; disabled fans emit no particles.
- [x] Scale emitter density by fan airflow and rate by backend inlet velocity.
- [x] Scale outlet indicators by solver airflow and velocity without inventing connecting trajectories.
- [x] Invalidate all fan and particle results after fan, inlet, or geometry edits.

Status: implementation and verification complete; awaiting Engineering UI Review. Nineteen frontend tests, strict TypeScript compilation, production build, 75 backend tests, nine canonical airflow goldens, single/dual/off fan behavior, affinity-law outputs, stale-state handling, and live WebGL result rendering all passed. EVE deliberately does not draw continuous redirection paths because the existing solver does not export spatial trajectories or per-fan outlet attribution.

This plan follows an ETIC rhythm for each sprint:

- **Explore:** confirm user problem, examples, constraints, and data.
- **Think:** compare options, record decisions and risks.
- **Implement:** build only the approved vertical slice.
- **Check:** test, validate with evidence, demonstrate, and hold a review gate.

No sprint starts implementation work whose prerequisite review gate is still open.

## Sprint 1 — Architecture and decision approval

Goal: approve a buildable and honest V1 contract.

### Explore

- [ ] Interview at least two HVAC engineers about the current fabrication loop.
- [ ] Collect anonymized example dimensions, inlet layouts, deflectors, and cell readings.
- [ ] Define V1-supported geometry and typical/maximum grid sizes.
- [ ] Confirm local desktop-like deployment versus hosted multi-user use.
- [x] Establish the biased-inlet 2 × 4, four-strong/four-weak deflector problem as the primary V1 acceptance scenario.

### Think

- [x] Draft product architecture and non-goals.
- [x] Draft modular-monolith system architecture and folder structure.
- [x] Draft data model, API, UI wireframes, and quality attributes.
- [x] Separate estimator results from conceptual animation.
- [x] Record ADR drafts for deployment, coordinates/units, revisions, engine boundary, knowledge, templates, and calibration.
- [x] Add D-08 Engineering Knowledge and Field Validation.
- [x] Clarify outlet-template ownership, baseline semantics, lifecycle, calibration applicability, validation wording, and deployment safety.
- [ ] Define engine validation acceptance criteria with engineering stakeholders.

### Implement

- [ ] No product code in this sprint before architecture approval.
- [ ] After document review only: create minimal repository/tooling scaffold as the first Sprint 2 task.

### Check / review gate

- [x] Review and approve decisions D-01 through D-08 in `ARCHITECTURE.md`.
- [x] Resolve every blocking architecture comment in the revised documents.
- [x] Approve terminology: estimated, measured, conceptual, calibrated, CFD-derived.
- [ ] Approve V1 acceptance criteria and explicit exclusions.
- [ ] Product owner accepts the required document revisions and marks Sprint 1 approved.

## Sprint 1.5 — Estimator technical spike and benchmark acquisition

Goal: retire the largest technical risk before investing in the full editor and production persistence.

### Explore / Think

- [ ] Acquire at least one measured field case with traceable test conditions.
- [ ] Agree candidate-ordering usefulness criteria and supported envelope.
- [ ] Define acceptable weak-cell improvement and maximum strong-cell reduction for the primary eight-cell case.
- [x] Draft `docs/validation/ESTIMATOR_SPIKE_PLAN.md`.
- [x] Define the pre-implementation solver architecture in `docs/validation/SOLVER_SPEC_V0.1.md`.
- [x] Prepare `docs/validation/HVAC_DOMAIN_REVIEW_PACKAGE.md` with equation classifications, physical-input inventory, and reviewer decisions.
- [ ] Review required physical inputs, symbolic equations, convergence residuals, output schema, and claim limits with an HVAC/domain specialist.

### Implement — isolated exploratory code only

- [ ] Define one shared immutable benchmark input format.
- [ ] Implement only an isolated conservation skeleton first: schemas, sequential extraction bookkeeping, residual reporting, and explicit unavailable values.
- [ ] Prototype parcel/ray and influence-matrix estimators in disposable isolated folders.
- [ ] Cover one plenum, one outlet grid, one inlet, and zero/one planar deflector.
- [ ] Parameterize deflector position, insertion length, width, and angle.
- [ ] Store deterministic benchmark inputs and outputs for symmetric, biased-inlet, primary eight-cell deflector, and measured cases.
- [ ] Emit all eight required comparison outputs, including intercepted fraction and redirected allocation with explicit estimate labels.

### Check / review gate

- [ ] Compare determinism, symmetry, runtime, explanation, sensitivity, calibration, measured ordering, and visualization suitability.
- [ ] Reject any prototype that calculates cells independently or cannot expose mass/momentum propagation and convergence residuals.
- [ ] Demonstrate whether the primary candidate improves the four weak cells without unacceptable loss in the four previously strong cells.
- [ ] Complete `docs/validation/ESTIMATOR_SPIKE_RESULTS.md` with limitations and recommendation.
- [ ] Select the simplest model meeting usefulness criteria, or stop if neither does.
- [ ] Explicitly approve Sprint 2; do not treat completion of prototype code as approval.

### Executable architecture milestones

- [x] Milestone 1 — Solver core framework with immutable inputs and provenance-bearing availability.
- [x] Milestone 2 — Geometry engine with structural validation and no automatic repair.
- [x] Milestone 3 — Control-volume builder using an explicit reviewed outlet order.
- [x] Milestone 4 — Solver state engine with governed lifecycle and sequential propagation.
- [x] Milestone 5 — Residual engine with injected evaluators and no built-in equations.
- [x] Milestone 6 — Convergence engine with injected criteria and no hidden tolerances.
- [x] Milestone 7 — Immutable conceptual result package with unavailable absolute quantities.
- [x] Milestone 8 — Read-only visualization interface and executable end-to-end skeleton.
- [x] Compile and run isolated/full standard-library unit tests after every milestone.

## Sprint 1.6 — Verification and benchmark framework

Goal: preserve solver contracts through permanent physics-free verification infrastructure.

- [x] Add governed verification-case schema and twelve canonical skeleton cases.
- [x] Add deterministic immutable golden snapshots with explicit two-flag update policy.
- [x] Add regression runner with pass, expected numerical failure, specification failure, unsupported, and non-zero regression exit.
- [x] Add invariant tests for availability, immutability, candidate isolation, visualization isolation, convergence safety, provenance, and determinism.
- [x] Add timing-only benchmark harness with runtime environment metadata and no thresholds.
- [x] Add empty documented future validation-dataset structure.
- [x] Record visualization-isolation defect correction in ADR-008.
- [x] Compile the complete Sprint 1.5/1.6 codebase successfully.
- [x] Pass all existing Sprint 1.5 and new Sprint 1.6 tests.
- [x] Demonstrate non-zero regression detection with an intentionally corrupted temporary fixture.
- [x] Verify golden files cannot be silently overwritten.
- [x] Publish `docs/validation/SPRINT_1_6_VERIFICATION_REPORT.md`.

## Sprint 1.7 — Geometry interaction evaluator

- [x] Publish the governed V0.1 evaluator specification.
- [x] Implement immutable path, deflector-frame, interaction, routing, provenance, diagnostic, and unavailable contracts.
- [x] Implement deterministic no/face/edge/corner/coplanar/blocked/invalid/unsupported classification.
- [x] Restrict routing to explicitly declared downstream control volumes.
- [x] Integrate through the existing candidate-state evaluator interface without mutating accepted state.
- [x] Add eleven deterministic interaction golden snapshots and regression runner.
- [x] Add property/invariant tests and timing-only benchmark stages.
- [x] Compile successfully and pass all Sprint 1.5, 1.6, and 1.7 tests.
- [x] Pass both framework and interaction regression runners.
- [x] Detect an intentionally corrupted interaction golden with non-zero status and unified diff.
- [x] Demonstrate unsupported geometry rejection and golden overwrite protection.
- [x] Publish `docs/validation/SPRINT_1_7_GEOMETRY_INTERACTION_REPORT.md`.

## Sprint 1.8 — Sequential extraction and mass conservation evaluator

- [x] Publish the governed V0.1 sequential extraction specification.
- [x] Implement immutable extraction, residual, provenance, diagnostic, policy, sequence, and adapter contracts.
- [x] Support only measured, prescribed-test, externally-evaluated, and unavailable sources with explicit provenance.
- [x] Implement explicit sequential current/candidate/accepted accounting and local/global residuals.
- [x] Keep unavailable distinct from available zero and reject over-extraction unconditionally.
- [x] Add fifteen deterministic conservation goldens and a dedicated regression runner.
- [x] Add conservation, rollback, provenance, availability, determinism, visualization-isolation, and forbidden-quantity tests.
- [x] Extend the timing-only benchmark harness without thresholds.
- [x] Compile and pass all Sprint 1.5 through Sprint 1.8 tests.
- [x] Pass all framework, geometry-interaction, and extraction regression runners.
- [x] Detect an intentionally corrupted conservation fixture with non-zero status and unified diff.
- [x] Verify unconfirmed golden overwrite rejection, zero/unavailable distinction, over-extraction rejection, and failed-middle isolation.
- [x] Publish `docs/validation/SPRINT_1_8_SEQUENTIAL_EXTRACTION_REPORT.md`.

## Sprint 2.0 — Experimental airflow solver V0.1

- [x] Define coordinate, inlet-direction, deflector-axis, and angle conventions before implementation.
- [x] Document engineering facts separately from experimental assumptions.
- [x] Implement replaceable distribution-kernel and deflector-influence interfaces.
- [x] Implement deterministic eight-outlet distribution, one-or-more deflector influence, supplied-CFM scaling, and sequential conservation.
- [x] Label all results and provenance as experimental/unvalidated.
- [x] Add six deterministic prototype goldens and verification tests.
- [x] Preserve all prior Sprint tests and regression runners.
- [x] Detect an intentionally corrupted prototype golden and reject unconfirmed golden updates.
- [x] Publish `AIRFLOW_SOLVER_V0.1.md` and the Sprint 2.0 report.
- [x] Stop after Sprint 2.0 and await review.

## Sprint 2 — Database and API foundation

Goal: scaffold the repository, persist trustworthy project/design revisions, and expose validated contracts.

### Explore / Think

- [ ] Validate aggregate boundaries with realistic projects.
- [ ] Decide draft auto-save and conflict behavior.
- [ ] Review SQLite backup, migration, and corruption-recovery expectations.

### Implement

- [ ] Scaffold FastAPI, settings, logging, tests, and migration tooling.
- [ ] Implement domain value objects, units, coordinates, and validation.
- [ ] Implement Project, Design, geometry, observation, and Deflector persistence.
- [ ] Implement mutable working-draft persistence without creating a Design per auto-save.
- [ ] Implement immutable EstimationRun snapshot persistence.
- [ ] Publish OpenAPI and generate TypeScript contracts.
- [ ] Add seed fixtures only from agreed synthetic examples.
- [ ] Do not implement outlet-template CRUD unless separately approved.
- [ ] Implement engineering-note/field-validation persistence only if Product Owner promotes it into Sprint 2 scope; otherwise preserve the boundary in migrations/contracts planning.

### Check / review gate

- [ ] Migration round-trip and clean-install tests pass.
- [ ] API/domain tests cover invalid geometry and revision conflicts.
- [ ] Snapshot reproducibility is demonstrated.
- [ ] No Three.js or HTTP types leak into the domain/engine interfaces.

## Sprint 3 — Geometry editor and project/design workflow

Goal: complete the design workflow with validated geometry, without simulation claims.

Polished airflow UI is blocked until the solver plan and Sprint 1.5 result are approved. Geometry/project workflow may proceed only after its own gate and must not synthesize engineering values.

### Explore / Think

- [ ] Test the wireframe with HVAC users using two representative tasks.
- [ ] Decide desktop minimum viewport and SI/IP switching behavior.

### Implement

- [ ] Build project list and design-revision workflow.
- [ ] Build outlet, air-box, inlet, and weak-cell editors.
- [ ] Build parametric deflector editing with numeric/direct manipulation sync.
- [ ] Build Three.js geometry scene, section view, selection, and camera controls.
- [ ] Add undo/redo, draft save, validation, accessibility, and reduced motion.

### Check / review gate

- [ ] Users complete a reference design without developer help.
- [ ] Keyboard and non-color workflows pass accessibility checks.
- [ ] Geometry round-trip matches API values within tolerance.
- [ ] No airflow animation is presented before numeric engine output exists.
- [ ] UI tests prove heat maps, gains/losses, rankings, recommendations, and airflow values are read from solver output without client-side engineering calculations.

## Sprint 4 — Validated estimation engine and numeric comparison

Goal: produce fast, deterministic, conservation-audited relative cell distributions, and absolute outputs only if validation permits.

### Explore / Think

- [ ] Build benchmark cases from measurements or controlled experiments.
- [ ] Reconfirm the Sprint 1.5 recommendation against expanded benchmark cases.

### Implement

- [ ] Implement chosen V1 engine and versioned configuration.
- [ ] Enforce coupled sequential extraction: deduct upstream extraction before downstream propagation.
- [ ] Implement documented pressure/resistance, deflector interaction, momentum update, and convergence methods only when their inputs and parameters have approved provenance.
- [ ] Emit explicit solver residuals, applicability, assumptions, missing inputs, unavailable fields, and claim level.
- [ ] Return aligned baseline/candidate shares, percentage-point deltas, weak improvement, strong reduction, estimated intercepted fraction, redirected allocation, validation state, contributions, and warnings.
- [ ] Add synchronous run API and immutable result persistence.
- [ ] Add baseline/candidate numeric and heat-map comparison.

### Check / review gate

- [ ] Determinism, symmetry, normalization, and golden tests pass.
- [ ] p95 runtime meets target within documented geometry limits.
- [ ] Validation report documents accuracy and unsupported cases.
- [ ] Primary 2 × 4 field scenario passes the approved comparative usefulness criteria.
- [ ] Stakeholders accept whether the engine remains experimental or can guide screening.

## Sprint 5 — Conceptual airflow visualization

Goal: explain engine output without overstating fidelity.

### Explore / Think

- [ ] User-test whether paths improve understanding or create false confidence.
- [ ] Define stable mapping from estimator parcels/contributions to presentation paths.

### Implement

- [ ] Render conceptual paths and particles from run output.
- [ ] Add play/pause, speed, density, section, heat-map, and reduced-motion behavior.
- [ ] Keep baseline/candidate scales and camera comparable.
- [ ] Display persistent result-kind and calibration labels.

### Check / review gate

- [ ] Animation never changes numeric results.
- [ ] Low-end reference hardware remains usable with adaptive visual density.
- [ ] Engineers can correctly explain what the animation does and does not mean.

## Sprint 6 — Performance improvements and conditional bounded candidate search

Goal: improve workflow and evaluate candidates safely; do not promise a global optimum.

### Explore / Think

- [ ] Profile real user sessions before optimizing performance.
- [ ] Define bounded parameters, constraints, and multi-objective trade-offs.
- [ ] Confirm engine validation is strong enough to justify automated search.

### Implement

- [ ] Optimize measured UI/API/engine bottlenecks.
- [ ] Add cached runs keyed by canonical input and engine version.
- [ ] If approved, add bounded candidate sweep with Pareto results for uniformity versus loss proxy.
- [ ] Add exportable design and assumption summary if prioritized.

### Check / review gate

- [ ] Before/after performance measurements show material gains.
- [ ] Candidate search respects fabrication and geometry constraints.
- [ ] Results are called recommendations/candidates, never guaranteed optima.
- [ ] Product release checklist and known-limitations document are approved.

## Cross-sprint definition of done

- [ ] Acceptance criteria and tests exist for each behavior.
- [ ] Units, coordinates, result provenance, and warnings remain explicit.
- [ ] API contract and architecture documentation are updated with decisions.
- [ ] Accessibility, error states, and performance are reviewed.
- [ ] No known result is presented with greater physical certainty than evidence supports.
- [ ] A review produces an explicit approve, revise, or stop decision.

## Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Convincing visuals imply CFD accuracy | Unsafe engineering confidence | Persistent labels, numeric-first comparison, validation report |
| No measured benchmark | Engine cannot be evaluated | Make dataset acquisition a Sprint 1/4 gate |
| Geometry scope expands into CAD | Schedule and UX failure | Freeze parametric V1 envelope |
| Optimization exploits proxy errors | Misleading recommendations | Gate search on validation; show Pareto candidates and constraints |
| SQLite used in multi-user deployment | Locking/data integrity problems | Keep local single-user assumption or revisit database/auth architecture |
| Unit/axis mismatch | Incorrect fabrication | Canonical SI and coordinate ADR; property and round-trip tests |
| Template library expands core V1 | Delivery delay without estimator value | Reserve boundary; require explicit scope promotion |
| Measurements mix with estimates | Invalid evidence and calibration | Separate entities, provenance labels, immutable runs |
