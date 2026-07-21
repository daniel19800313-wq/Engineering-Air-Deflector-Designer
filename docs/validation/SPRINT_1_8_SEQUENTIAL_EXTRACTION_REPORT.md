# Sprint 1.8 Sequential Extraction Report

Status: Complete — governed conservation evaluator baseline

## Implemented architecture

- Immutable extraction input, instruction, local result, sequence result, residual, policy, provenance, diagnostic, and state-adapter contracts.
- Explicit sequential evaluator that validates one instruction per declared outlet, creates a candidate local accounting record, accepts it only after conservation comparison, and propagates accepted downstream state.
- Public conservation evaluator for explicit local/global candidate accounting.
- Existing outlet-extraction protocol adapter preserving current/candidate/accepted separation and passing pressure/momentum through unchanged by identity.
- Dedicated regression runner, deterministic golden snapshots, invariant tests, and timing-only benchmark extensions.

## Supported quantity semantics and sources

One explicitly unit-labelled scalar transported quantity across one explicit linear outlet order. Permitted extraction sources are `measured`, `prescribed_test_input`, `externally_evaluated`, and `unavailable`. Sprint fixtures use only `prescribed_test_input` and are not HVAC predictions.

Every available extraction requires existing `EngineeringValue` provenance plus extraction source/reference/evaluator provenance. Unavailable remains distinct from available zero.

## Conservation behavior

The evaluator applies only reviewed local/global subtraction accounting. Local incoming, extraction, downstream, and residual remain visible. Global inlet, accepted total extraction, terminal downstream, and residual remain visible. Residual comparison uses an explicit unit, tolerance, tolerance provenance, and evaluator version with no defaults.

Unavailable operands create unavailable residuals and never imply conservation. Extraction greater than current incoming is always rejected; residual tolerance cannot authorize over-extraction. Failed middle candidates preserve only prior accepted records, mark the sequence incomplete, and leave terminal/total completion quantities unavailable.

## Case and golden inventory

Fifteen deterministic goldens:

1. One prescribed outlet.
2. Multiple sequential outlets.
3. Available zero extraction.
4. Unavailable inlet.
5. Unavailable extraction.
6. Missing extraction provenance.
7. Negative extraction.
8. Extraction exceeding incoming.
9. Duplicate instruction.
10. Undeclared outlet.
11. Explicit order mismatch.
12. Failed middle-outlet isolation.
13. Explicit local residual failure.
14. Explicit global residual failure.
15. Unavailable conservation residual.

Tests additionally cover local/global success and deliberately inconsistent candidates, unavailable residual behavior, zero/unavailable distinction, adapter identity, deterministic payloads, forbidden-quantity absence, recommendation absence, and corrupted-golden detection.

## Invariant inventory

- Accepted local records satisfy the explicit comparison policy.
- Global accounting is derived from the accepted chain.
- Unavailable never becomes zero; available zero remains available.
- Extraction cannot be negative, non-finite, unit-incompatible, unprovenanced, or greater than incoming.
- Duplicate, undeclared, missing, or misordered instructions are rejected.
- A rejected candidate cannot alter accepted state.
- Each downstream input is the previous accepted downstream output.
- Provenance survives input, local, global, golden, and adapter boundaries.
- No pressure, resistance, velocity, aerodynamics, recommendation, or predicted distribution is created.
- Failed/aborted solver packages remain isolated from visualization by the existing terminal-result contract.

## Golden and benchmark policy

Goldens use the shared versioned deterministic serializer, contain labelled prescribed fixture values with unit/provenance, omit timestamps, require confirmed update, and produce unified diffs. The benchmark measures validation, one step, multi-outlet execution, local/global packaging, and provenance packaging. Timing has no threshold or validation meaning.

## Known limitations

- Extraction is supplied rather than predicted.
- Only one linear scalar sequence and one shared unit are supported.
- No unit conversion, leakage, intermediate source, branching, reverse transport, uncertainty propagation, or density transformation exists.
- The evaluator does not decide whether measured/external evidence is representative.
- Comparison tolerance governance for production evidence remains unresolved.

## Unresolved engineering questions

- Which reviewed future evaluator supplies extraction instructions?
- Which conserved scalar/unit is valid for each deployment and operating condition?
- How should measurement uncertainty affect residual comparison without hiding imbalance?
- How should leakage or density changes be represented if later admitted?
- What evidence permits measured and externally evaluated sources to enter engineering-use workflows?

## Sprint 1.9 entry criteria

- This specification/report and extraction-source governance are approved.
- The source and unit semantics of the next evaluator are reviewed.
- Any production residual tolerance has explicit derivation, provenance, and applicability.
- Calibration and validation fixtures remain separate from prescribed contract tests.
- No extraction prediction is introduced without a separately reviewed physical model.
- Existing rollback, availability, provenance, visualization-isolation, and no-recommendation invariants remain mandatory.

## Validation statement

**Sprint 1.8 validates explicit sequential accounting and conservation contracts only. Outlet extraction has not been physically predicted or validated. No airflow distribution, pressure, resistance, velocity, deflector aerodynamics, grille behavior, coefficient, or HVAC performance has been validated.**
