# ADR-005: Engineering notes and field validation

## Context
Field observations and measurements are essential for engineering learning and calibration but are not estimator outputs.

## Decision
Preserve EngineeringNote, FieldValidation, and FieldCellMeasurement as separate traceable entities linked to Project, Design, and optionally EstimationRun. Never overwrite run results. Label estimated, measured, engineer-classified, and CFD-derived sources explicitly. Defer binary attachments and keep knowledge records out of the core engine contract.

## Alternatives considered
Store measurements in CellResult; put all evidence in unstructured project notes; build a full attachment/calibration platform now.

## Consequences
Evidence stays trustworthy and future calibration is possible. Additional CRUD may be deferred; relational integrity and provenance validation are required when implemented.

## Reversibility
High. Optional entities can be introduced incrementally without changing immutable run semantics.

## Status
Accepted in conditional Sprint 1 review; Sprint 2 implementation scope remains a Product Owner decision.
