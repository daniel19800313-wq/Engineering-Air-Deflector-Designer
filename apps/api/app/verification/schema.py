"""Governed verification-case schema and strict JSON loader."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


CASE_SCHEMA_VERSION = "add-verification-case-v1"


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class ExpectedContract:
    """Non-physical contract expectations for one verification case."""
    status: str
    diagnostics: tuple[str, ...]
    claim_level: str
    confidence_level: str
    available_quantities: tuple[str, ...]
    unavailable_quantities: tuple[str, ...]
    provenance_requirements: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VerificationCase:
    """Immutable governed case containing inputs and contract expectations only."""
    schema_version: str
    case_id: str
    description: str
    geometry_input: Mapping[str, object]
    control_volume_order: tuple[str, ...] | None
    boundary_condition_availability: Mapping[str, object]
    evaluator_configuration: Mapping[str, object]
    expected: ExpectedContract
    applicability_envelope: Mapping[str, object]
    golden_snapshot: str | None


def load_case(path: Path) -> VerificationCase:
    """Load and validate a case; unknown engineering expectations are not inferred."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != CASE_SCHEMA_VERSION:
        raise ValueError(f"unsupported case schema: {raw.get('schema_version')}")
    required = {"case_id", "description", "geometry_input", "boundary_condition_availability", "evaluator_configuration", "expected", "applicability_envelope"}
    missing = sorted(required - raw.keys())
    if missing:
        raise ValueError(f"missing required case fields: {', '.join(missing)}")
    expected = _mapping(raw["expected"], "expected")
    order = raw.get("control_volume_order")
    if order is not None and not isinstance(order, list):
        raise ValueError("control_volume_order must be an array or null")
    return VerificationCase(
        CASE_SCHEMA_VERSION,
        str(raw["case_id"]),
        str(raw["description"]),
        _mapping(raw["geometry_input"], "geometry_input"),
        tuple(str(item) for item in order) if order is not None else None,
        _mapping(raw["boundary_condition_availability"], "boundary_condition_availability"),
        _mapping(raw["evaluator_configuration"], "evaluator_configuration"),
        ExpectedContract(
            str(expected["status"]),
            tuple(str(item) for item in expected.get("diagnostics", [])),
            str(expected["claim_level"]),
            str(expected["confidence_level"]),
            tuple(str(item) for item in expected.get("available_quantities", [])),
            tuple(str(item) for item in expected.get("unavailable_quantities", [])),
            tuple(str(item) for item in expected.get("provenance_requirements", [])),
        ),
        _mapping(raw["applicability_envelope"], "applicability_envelope"),
        str(raw["golden_snapshot"]) if raw.get("golden_snapshot") else None,
    )


def load_cases(directory: Path) -> tuple[VerificationCase, ...]:
    """Load cases deterministically by filename."""
    return tuple(load_case(path) for path in sorted(directory.glob("*.json")))

