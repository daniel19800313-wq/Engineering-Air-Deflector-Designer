"""Deterministic golden serialization and deliberate update policy."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


GOLDEN_SCHEMA_VERSION = "add-golden-result-v1"


def serialize_golden(payload: Mapping[str, object]) -> str:
    """Serialize without timestamps or platform noise using stable key ordering."""
    governed = {"schema_version": GOLDEN_SCHEMA_VERSION, "result": dict(payload)}
    return json.dumps(governed, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def compare_golden(path: Path, payload: Mapping[str, object]) -> tuple[bool, str]:
    """Return deterministic comparison and a readable line-oriented diff."""
    expected = path.read_text(encoding="utf-8") if path.exists() else "<missing golden>\n"
    actual = serialize_golden(payload)
    if expected == actual:
        return True, ""
    import difflib
    diff = "".join(difflib.unified_diff(expected.splitlines(True), actual.splitlines(True), fromfile=str(path), tofile="actual"))
    return False, diff


def update_golden(path: Path, payload: Mapping[str, object], *, confirmed: bool) -> None:
    """Write a golden only after the caller supplies explicit confirmation."""
    if not confirmed:
        raise PermissionError("golden update requires explicit confirmation")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_golden(payload), encoding="utf-8", newline="\n")

