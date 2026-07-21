"""Executable, physics-free ADD solver framework.

The package owns solver lifecycle and engineering-data provenance.  Physics
models are intentionally absent from Sprint 1.5.
"""

from .core import (
    Availability,
    Diagnostic,
    DiagnosticSeverity,
    EngineeringValue,
    Provenance,
    RunInputSnapshot,
    SolverMode,
)

__all__ = [
    "Availability",
    "Diagnostic",
    "DiagnosticSeverity",
    "EngineeringValue",
    "Provenance",
    "RunInputSnapshot",
    "SolverMode",
]

