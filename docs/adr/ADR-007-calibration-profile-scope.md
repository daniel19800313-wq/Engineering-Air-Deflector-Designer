# ADR-007: Calibration profile scope

## Context
Calibration coefficients are valid only for the model version, geometry family, parameter bounds, and evidence used to derive them.

## Decision
Store versioned calibration profiles as global reference data tied to engine identity/version compatibility and an explicit validated geometry-family envelope. Runs select profiles explicitly and the engine checks applicability. Never silently inherit a profile across projects or extrapolate it outside its envelope. Use explicit validation states rather than a confidence score.

## Alternatives considered
Project-owned profiles; one global default; geometry-independent coefficients; opaque confidence score.

## Consequences
Reuse is controlled and provenance remains clear. Applicability metadata and envelope checks add work; outside-envelope runs are explicitly labeled.

## Reversibility
Moderate. Ownership can expand later, but historical runs retain calibration ID/version and state.

## Status
Accepted in conditional Sprint 1 review.
