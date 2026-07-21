# ADR-006: Outlet template ownership

## Context
Engineers reuse outlet products, but template edits must not mutate historical designs or results.

## Decision
Reserve a global local-library OutletTemplate concept. Creating a design copies template geometry into the design snapshot and may retain provenance. No live reference or propagation is allowed. Treat the library as post-core-V1 and do not implement it in Sprint 2 without explicit approval.

## Alternatives considered
Sprint 2 full template CRUD; project-owned templates; designs reference mutable templates directly.

## Consequences
The ownership boundary is safe without adding immediate scope. Users recreate common geometry until the library is promoted.

## Reversibility
High because copied geometry is already self-contained; a library can be added later.

## Status
Accepted in conditional Sprint 1 review.
