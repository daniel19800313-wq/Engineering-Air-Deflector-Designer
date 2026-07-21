# ADD Verification Framework

Cases under `cases/` are governed, physics-free contract fixtures. Goldens under `goldens/` are deterministic snapshots without timestamps. They contain status, diagnostics, availability, provenance, and claim contracts—not airflow expectations.

Run regressions from `apps/api`:

```text
python -m app.verification.runner
```

Golden updates are never automatic. A deliberate update requires both flags and review of the resulting diff:

```text
python -m app.verification.runner --update-golden --confirm-update
```

The runner reports `PASS`, `FAIL [specification failure]`, and `UNSUPPORTED`. Solver numerical failures remain expected payload states when a case specifies them; disagreement with the case/golden is a specification regression and returns a non-zero process status.

Run timing-only benchmarks:

```text
python benchmarks/run_benchmarks.py
```

Benchmark output is environment-tagged JSON. No timing threshold or engineering validation conclusion is applied.
