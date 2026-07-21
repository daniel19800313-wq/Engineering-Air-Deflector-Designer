# ADR-004: Estimation engine boundary

## Context
The estimator is the largest uncertainty, must remain non-CFD, and may later be replaced or complemented by calibrated models or CFD.

## Decision
Use a deterministic, I/O-free engine contract from immutable input snapshot to immutable result snapshot. Keep presentation animation separate. Run a time-boxed Sprint 1.5 comparison of parcel/ray and influence-matrix prototypes before selecting the production engine. Exclude pressure-loss proxy until defensible and validated.

## Alternatives considered
Select parcel/ray immediately; use UI particle behavior as the estimator; integrate CFD in V1.

## Consequences
The project confronts feasibility early and preserves replaceability. A short prototype investment precedes repository implementation.

## Reversibility
High because engine implementations sit behind a versioned contract; persisted snapshots preserve old results.

## Status
Accepted in conditional Sprint 1 review; production model remains undecided pending Sprint 1.5.
