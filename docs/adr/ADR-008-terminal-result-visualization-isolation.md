# ADR-008: Terminal result visualization isolation

## Context
Sprint 1.6 verification found that the Sprint 1.5 adapter could expose unavailable outlet objects from a failed result. Although no fabricated value was shown, this violated the approved rule that failed iterations never reach visualization.

## Decision
The visualization adapter exports outlet engineering cells only from a `converged` result package. Failed and aborted packages expose terminal status and diagnostics but an empty cell payload. Value-identity verification uses a converged conceptual package and does not imply validated physics.

## Alternatives considered
Expose unavailable failed cells; add a UI-only filter; allow callers to opt in.

## Consequences
Failure isolation is enforced at the solver boundary instead of relying on UI behavior. The existing visualization payload type remains compatible, but failed-result cell content changes to empty.

## Reversibility
High, but relaxing this boundary would require architecture review and a safe diagnostic-specific contract.

## Status
Accepted as a Sprint 1.6 defect correction required by the approved execution architecture.
