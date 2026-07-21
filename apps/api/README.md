# ADD Solver Skeleton

`app.solver` is the executable Sprint 1.5 framework. It intentionally contains no reviewed physics equations, coefficient values, pressure/resistance defaults, or fabricated engineering results.

Public modules:

- `core`: immutable run input, provenance, diagnostics, and available/unavailable engineering values.
- `geometry`: V0.1 geometry contracts and structural validation.
- `control_volume`: explicit ordered control-volume topology.
- `state`: lifecycle state machine, segment/outlet state, injected physics protocols, and sequential propagation.
- `residuals`: injected residual-evaluator interface and reports.
- `convergence`: injected criterion interface and convergence decisions without hidden tolerances.
- `results`: immutable conceptual result packaging and claim/confidence categories.
- `framework`: top-level lifecycle runner with explicit execution policy.
- `visualization`: read-only projection of solver-owned result values.

The skeleton is executable but fails safely when physics/residual quantities are unavailable. Future physics modules must implement the documented protocols and pass domain review without changing these structural contracts.

Run the isolated standard-library test suite from `apps/api` with the configured Python runtime:

```text
python -m unittest discover -s tests -p test_*.py -v
```

## Simulation workspace API

Install `requirements.txt`, then run the HTTP adapter from this directory:

```text
python -m uvicorn app.main:app --reload
```

The Sprint 2.1 workspace uses `POST /api/v1/simulations/airflow`. The endpoint
adapts explicit UI inputs to the existing Experimental Airflow Solver V0.1 and
returns availability-aware engineering values and provenance.
