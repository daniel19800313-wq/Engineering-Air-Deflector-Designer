# ADR-003: Mutable drafts, saved designs, and immutable runs

## Context
Auto-save, deliberate engineering checkpoints, and reproducible calculations have different lifecycle needs.

## Decision
Auto-save updates a mutable working draft. A user checkpoint creates a named saved Design revision. An EstimationRun is immutable and contains the complete input snapshot and provenance. Baseline is a per-comparison run selection, never a global flag.

## Alternatives considered
Create a Design revision on every auto-save; keep only one mutable Design; mark one project-wide baseline.

## Consequences
History remains meaningful and runs reproducible. Draft recovery and concurrency need explicit handling. Comparison selects two compatible runs.

## Reversibility
Moderate if lifecycle fields and snapshots exist from the first migration.

## Status
Accepted in conditional Sprint 1 review.
