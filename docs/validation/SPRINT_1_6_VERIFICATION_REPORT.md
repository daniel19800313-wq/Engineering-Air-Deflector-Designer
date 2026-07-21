# Sprint 1.6 Verification Report

Status: Complete — verification framework baseline

## Implemented verification architecture

- Strict immutable JSON case schema with explicit version, geometry input, outlet order, boundary availability, evaluator scenario, contract expectations, provenance requirements, and applicability metadata.
- Twelve physics-free canonical cases executed through solver public contracts.
- Deterministic golden serializer with sorted keys, stable formatting, explicit schema version, and no timestamps.
- Golden comparison with unified diffs and a deliberate two-flag update command.
- Regression runner reporting pass, expected numerical failure, specification failure, and unsupported; specification/golden regressions return a non-zero process status.
- Property/invariant tests alongside all Sprint 1.5 tests.
- Standard-library timing harness with runtime environment metadata and no performance gates.
- Empty, documented future validation-dataset structure with calibration/holdout separation.

Sprint 1.6 found and corrected one public-contract defect: failed result packages could expose unavailable outlet objects to visualization. ADR-008 records the correction; failed/aborted packages now expose no visualization cells.

## Case inventory

1. Valid geometry with unavailable physics.
2. Invalid geometry.
3. Missing explicit outlet order.
4. Unavailable residual evaluator/result.
5. Unavailable convergence criteria.
6. Forced non-converged run.
7. Candidate-state rejection.
8. Accepted-state commit.
9. Failed partial-iteration isolation.
10. Unavailable absolute airflow.
11. Conceptual result cannot recommend.
12. Visualization preserves original solver-value identity for a converged package.

These cases assert framework contracts only. They contain no approved or unapproved airflow distribution, pressure, resistance, coefficient, or convergence-tolerance expectation.

## Invariant inventory

- Available values require provenance.
- Unavailable values contain no value and never become zero.
- Run-input mappings are recursively immutable.
- Invalid or non-finite geometry is rejected without repair.
- Explicit outlet order contains every cell exactly once.
- Every outlet consumes the current downstream state.
- Rejected candidates are not accepted or packaged as successful state.
- Failed runs expose no visualization cells.
- Non-converged/conceptual results cannot recommend.
- Missing residual evaluators or criteria cannot imply convergence.
- Input/solver provenance survives case execution and golden serialization.
- UI-facing payloads are frozen and preserve solver value identity.
- Repeated deterministic inputs produce byte-identical golden serialization.

## Golden-result policy

- Schema: `add-golden-result-v1`.
- Goldens include contract status, diagnostics, claim/confidence, availability, provenance identifiers, and recommendation eligibility only.
- Timestamps, timing results, host paths, and other nondeterministic metadata are excluded.
- Ordinary regression execution is read-only.
- Updates require both `--update-golden` and `--confirm-update`.
- The update API refuses writes without explicit confirmation; tests verify an existing file remains byte-identical.
- Changes must be deliberately generated and reviewed; the runner never overwrites a mismatch automatically.
- Twelve canonical golden snapshots exist. None contains engineering values.

## Regression policy

An expected solver `failed` status can pass a case and is reported as an expected numerical failure. A mismatch against the governed contract or golden is a specification failure and returns non-zero. Unsupported capability is reported separately and is not silently treated as pass or an engineering result.

The test suite creates an intentionally corrupted case whose expected status disagrees with execution. The runner reports a specification failure and returns non-zero. This fixture exists only in a temporary test directory and never overwrites canonical cases/goldens.

## Benchmark policy

The harness measures only:

- geometry validation;
- control-volume graph construction;
- state initialization;
- one unavailable-physics skeleton iteration;
- result packaging;
- visualization projection.

It reports elapsed timing and Python implementation/version, platform, processor string, and logical CPU count. It defines no pass/fail threshold, persists no automatic baseline, and provides no HVAC validation evidence. Timing results must remain separate from engineering validation datasets and golden contracts.

Commands from `apps/api` using the configured Python runtime:

```text
python -m app.verification.runner
python benchmarks/run_benchmarks.py
python -m unittest discover -s tests -p test_*.py -v
```

Deliberate golden update only:

```text
python -m app.verification.runner --update-golden --confirm-update
```

## Validation dataset structure

`datasets/validation/` reserves empty, documented directories for site geometry, TAB measurements, instrument metadata, baseline cases, candidate-deflector cases, calibration cases, holdout validation cases, and CFD comparison cases. No measurement has been fabricated or populated.

## Known limitations and unresolved risks

- Canonical cases exercise structural scenarios, not HVAC behavior.
- Scenario adapters are deliberately physics-free and cannot establish mass, momentum, pressure, resistance, or airflow validity.
- No residual equation or convergence criterion is available; expected failed states dominate the current cases.
- Case JSON validation is strict at the governed field level but is not yet backed by an external JSON Schema artifact.
- Golden review remains a human process; repository branch protection/CI policy is not configured in this sprint.
- The single-path outlet order is supplied explicitly; no reviewed physics determines it.
- Timing samples are lightweight observations, not statistically stable performance baselines.
- Dataset governance still needs privacy/access, raw-file immutability, and measurement uncertainty procedures before field data arrives.

## Sprint 1.7 entry criteria

- Sprint 1.6 report and ADR-008 accepted.
- Canonical cases and goldens reviewed for contract meaning.
- CI/repository policy chosen for tests and golden changes.
- First future evaluator has HVAC-domain approval, named equation/relationship provenance, explicit inputs, and applicability envelope.
- Residual definitions and convergence criteria are reviewed before any converged physics case is added.
- Calibration and holdout datasets remain separated before model fitting/evaluation.
- Any new engineering expectation is traceable to approved physics and evidence; otherwise it remains unavailable.

## Verification statement

Compilation succeeded. All existing Sprint 1.5 tests and new Sprint 1.6 tests pass. The canonical regression suite passes, the intentional corruption test returns non-zero, and unconfirmed golden overwrite is rejected.

**No HVAC physics, airflow distribution, pressure model, resistance model, coefficient, convergence tolerance, absolute airflow, or engineering accuracy has been validated by Sprint 1.6.**
