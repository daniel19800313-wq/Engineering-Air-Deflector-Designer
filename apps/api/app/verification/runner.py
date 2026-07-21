"""Command-line regression runner for verification cases and goldens."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from typing import Mapping

from .golden import compare_golden, update_golden
from .schema import VerificationCase, load_cases
from .scenarios import execute_case


def _contract_failures(case: VerificationCase, payload: Mapping[str, object]) -> list[str]:
    failures: list[str] = []
    comparisons = {
        "status": case.expected.status,
        "claim_level": case.expected.claim_level,
        "confidence_level": case.expected.confidence_level,
        "available_quantities": list(case.expected.available_quantities),
        "unavailable_quantities": list(case.expected.unavailable_quantities),
    }
    for field, expected in comparisons.items():
        if payload.get(field) != expected:
            failures.append(f"{field}: expected {expected!r}, got {payload.get(field)!r}")
    actual_diagnostics = set(payload.get("diagnostics", []))
    for code in case.expected.diagnostics:
        if code not in actual_diagnostics:
            failures.append(f"missing diagnostic: {code}")
    provenance = payload.get("provenance", {})
    for field in case.expected.provenance_requirements:
        if not isinstance(provenance, Mapping) or field not in provenance:
            failures.append(f"missing provenance: {field}")
    return failures


def run_cases(case_dir: Path, golden_dir: Path, *, update: bool = False, confirmed: bool = False) -> int:
    """Run every case and return non-zero on specification or golden regression."""
    failed = 0
    unsupported = 0
    for case in load_cases(case_dir):
        result = execute_case(case)
        if result.unsupported:
            unsupported += 1
            print(f"UNSUPPORTED {case.case_id}")
            continue
        failures = _contract_failures(case, result.payload)
        golden_path = golden_dir / (case.golden_snapshot or f"{case.case_id}.json")
        if update:
            update_golden(golden_path, result.payload, confirmed=confirmed)
        elif case.golden_snapshot:
            matches, diff = compare_golden(golden_path, result.payload)
            if not matches:
                failures.append("golden mismatch\n" + diff)
        if failures:
            failed += 1
            print(f"FAIL {case.case_id} [specification failure]")
            for failure in failures:
                print(f"  {failure}")
        else:
            classification = " [expected numerical failure]" if result.payload.get("status") == "failed" else ""
            print(f"PASS {case.case_id}{classification}")
    print(f"SUMMARY pass={len(load_cases(case_dir)) - failed - unsupported} fail={failed} unsupported={unsupported}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ADD physics-free solver verification cases.")
    parser.add_argument("--cases", type=Path, default=Path("verification/cases"))
    parser.add_argument("--goldens", type=Path, default=Path("verification/goldens"))
    parser.add_argument("--update-golden", action="store_true")
    parser.add_argument("--confirm-update", action="store_true")
    args = parser.parse_args()
    if args.confirm_update and not args.update_golden:
        parser.error("--confirm-update requires --update-golden")
    return run_cases(args.cases, args.goldens, update=args.update_golden, confirmed=args.confirm_update)


if __name__ == "__main__":
    raise SystemExit(main())
