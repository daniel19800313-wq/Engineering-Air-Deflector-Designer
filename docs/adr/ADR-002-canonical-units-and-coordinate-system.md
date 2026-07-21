# ADR-002: Canonical units and coordinate system

## Context
HVAC inputs may use SI or IP units, while geometry and fabrication errors can result from implicit conversions or axes.

## Decision
Persist SI: metres, m³/s, and Pa. Accept/display user-selected units with explicit conversion. Use a right-handed system: X left-to-right across the outlet, Y bottom-to-top, Z from outlet into plenum; inlet direction points into the plenum. API angles use degrees.

## Alternatives considered
Persist user-entered units; millimetre-only geometry; Three.js-native coordinates without a domain convention.

## Consequences
Calculations and snapshots are consistent, while all boundaries require tested conversion. UI must always display units.

## Reversibility
Low after persisted data exists; conversion migrations are possible but risky.

## Status
Accepted in conditional Sprint 1 review.
