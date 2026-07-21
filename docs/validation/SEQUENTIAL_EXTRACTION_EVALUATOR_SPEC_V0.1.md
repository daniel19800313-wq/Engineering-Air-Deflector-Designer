# Sequential Extraction Evaluator Specification V0.1

Status: Sprint 1.8 governed conservation specification

## Purpose and scope

Account for an explicitly available transported quantity through an explicitly ordered outlet sequence. Each extraction is supplied by a governed external source; the evaluator validates, subtracts, reports residuals, and propagates only accepted downstream state. It does not predict extraction.

## Inputs and transported-quantity semantics

- Available or explicitly unavailable inlet `EngineeringValue`.
- Exact declared outlet order and matching declared outlet set.
- One instruction per outlet with available/unavailable extraction, unit, and source provenance.
- Explicit policy containing unit semantics, comparison tolerance, tolerance provenance, and evaluator version. There are no defaults.

The transported quantity is an abstract conserved scalar using the caller-declared unit. It becomes mass flow, volume flow, or another engineering quantity only when its supplied source and unit legitimately say so. Test fixtures are prescribed evidence, not predicted HVAC behavior.

## Sequential and conservation relationships

For each current outlet, the approved local relationship is restated from the reviewed baseline: downstream remaining quantity equals incoming quantity less explicitly supplied extraction. Local residual exposes incoming less extraction less downstream. After all accepted outlets, global residual exposes inlet less total accepted extraction less terminal downstream.

Unavailable operands produce unavailable residuals and `conserved = unavailable`. A residual is conserved only through the explicitly injected comparison tolerance and provenance. Reaching the last outlet does not imply conservation.

## Outputs

- Per outlet: incoming, extracted, downstream, explicit residual/comparison result, outlet identity, and extraction provenance.
- Sequence: completed flag, accepted local chain, inlet, total accepted extraction, terminal downstream, global residual, diagnostics, and fixed absent recommendation.
- Failed sequences preserve accepted local records for diagnostics but mark total/terminal unavailable unless a completed governed result exists. They are never exported as completed visualization results.

## Extraction-source governance

Permitted sources: `measured`, `prescribed_test_input`, `externally_evaluated`, and `unavailable`. Available values require both existing value provenance and extraction-source provenance. Unknown, missing, or inferred amounts are forbidden.

## Availability rules

- Unavailable inlet cannot generate downstream values.
- Unavailable extraction stops the sequence; it is not zero.
- Available zero is valid and distinct from unavailable.
- Missing provenance, incompatible units, negative/non-finite values, extraction above incoming, undeclared/duplicate/missing outlets, and order mismatches are rejected.
- Partial availability remains explicit; no repair or replacement occurs.

## Candidate-state integration

`ExtractionStateAdapter` implements the existing outlet extraction protocol. It consumes current `SegmentState.remaining_flow`, evaluates one declared instruction, and returns a new candidate `OutletState`. Pressure and momentum values pass through by identity without interpretation. Failure raises before candidate acceptance and cannot mutate incoming accepted state.

## Provenance and residual semantics

Every supplied extraction retains source type/reference and evaluator version. Calculated remaining/total/residual values identify the authorized conservation-accounting relationship and evaluator version. Comparison tolerance has its own mandatory provenance. Residual availability and conservation decision are separate.

## Failure contract and applicability envelope

V0.1 supports one finite explicitly ordered linear outlet sequence, one scalar unit shared by inlet/instructions/policy, and one explicit instruction per outlet. Any rejected local candidate ends completion, preserves prior accepted records, and exposes a stable diagnostic. Multiple branches, reverse transport, unit conversion, leakage, sources between outlets, and coupled networks are outside the envelope.

## Known limitations

- Extraction amounts are supplied, never predicted.
- No uncertainty propagation is implemented.
- Floating-point comparison depends on the explicit governed tolerance.
- The evaluator does not decide whether measured/prescribed evidence is physically representative.
- Volume-flow conservation across changing density is not established by this abstract scalar contract.

## Validation strategy

Canonical fixtures cover prescribed single/multiple/zero extraction, unavailable and invalid inputs, order/provenance governance, local/global residual behavior, rollback, determinism, provenance, visualization isolation, and recommendation prohibition. Goldens contain labelled test quantities only and make no HVAC distribution claim.

## Explicit exclusions

Pressure, resistance, velocity, density conversion, grille behavior, extraction ratio/coefficient, deflector aerodynamics, turbulence, leakage modeling, optimization, predicted distribution, recommendations, and relative or absolute HVAC performance claims.
