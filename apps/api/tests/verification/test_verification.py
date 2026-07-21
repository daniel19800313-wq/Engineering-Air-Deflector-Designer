"""Contract, golden, determinism, and regression-detection tests."""
import json
import tempfile
import unittest
from pathlib import Path

from app.verification.golden import compare_golden, serialize_golden, update_golden
from app.verification.runner import run_cases
from app.verification.schema import load_case, load_cases
from app.verification.scenarios import execute_case
from app.solver.core import Availability, EngineeringValue


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "verification" / "cases"
GOLDENS = ROOT / "verification" / "goldens"


class VerificationSchemaTests(unittest.TestCase):
    def test_all_canonical_cases_load(self) -> None:
        cases = load_cases(CASES)
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({case.case_id for case in cases}), len(cases))

    def test_deterministic_input_produces_deterministic_contract(self) -> None:
        case = load_case(CASES / "01-valid-unavailable-physics.json")
        first = execute_case(case).payload
        second = execute_case(case).payload
        self.assertEqual(serialize_golden(first), serialize_golden(second))


class AvailabilityInvariantTests(unittest.TestCase):
    def test_unavailable_never_becomes_zero(self) -> None:
        value = EngineeringValue[float].unavailable("not calculated", "m3/s")
        self.assertEqual(value.availability, Availability.UNAVAILABLE)
        self.assertIsNone(value.value)
        self.assertNotEqual(value.value, 0)

    def test_case_provenance_survives_execution(self) -> None:
        case = load_case(CASES / "01-valid-unavailable-physics.json")
        provenance = execute_case(case).payload["provenance"]
        self.assertEqual(provenance["input_run_id"], case.case_id)


class GoldenPolicyTests(unittest.TestCase):
    def test_golden_update_requires_confirmation_and_cannot_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "golden.json"
            original = "existing\n"
            path.write_text(original, encoding="utf-8")
            with self.assertRaises(PermissionError):
                update_golden(path, {"status": "changed"}, confirmed=False)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_comparison_does_not_modify_golden(self) -> None:
        path = GOLDENS / "valid-unavailable-physics.json"
        before = path.read_bytes()
        compare_golden(path, {"corrupted": True})
        self.assertEqual(path.read_bytes(), before)


class RegressionRunnerTests(unittest.TestCase):
    def test_runner_detects_intentionally_corrupted_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            case_dir = Path(directory) / "cases"
            case_dir.mkdir()
            raw = json.loads((CASES / "01-valid-unavailable-physics.json").read_text(encoding="utf-8"))
            raw["expected"]["status"] = "converged"
            raw["golden_snapshot"] = None
            (case_dir / "corrupted.json").write_text(json.dumps(raw), encoding="utf-8")
            self.assertNotEqual(run_cases(case_dir, Path(directory) / "goldens"), 0)


if __name__ == "__main__":
    unittest.main()
