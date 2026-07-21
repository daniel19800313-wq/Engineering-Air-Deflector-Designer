# Future ADD Validation Dataset

This directory is intentionally empty of engineering measurements. Never add synthetic values that could be mistaken for site evidence.

Structure:

- `site_geometry/`: surveyed/drawing geometry with source, revision, units, and coordinate metadata.
- `tab_measurements/`: traceable Testing, Adjusting and Balancing observations.
- `instrument_metadata/`: model, serial/calibration record, method, accuracy, and measurement position.
- `baseline_cases/`: pre-deflector operating cases linked to geometry and operating conditions.
- `candidate_deflector_cases/`: candidate geometry and measurements linked to a baseline.
- `calibration_cases/`: explicitly designated fitting data; never reused as holdout evidence.
- `holdout_validation_cases/`: locked independent evaluation data.
- `cfd_comparison_cases/`: documented CFD domains, meshes, boundaries, convergence, and mappings.

Each future case requires stable IDs, provenance, consent/access classification, units, timestamps from the source record, operating condition, missing-data declarations, and immutable raw evidence. Derived datasets must reference raw inputs and the transformation version. Calibration/holdout membership must be assigned before model evaluation.
