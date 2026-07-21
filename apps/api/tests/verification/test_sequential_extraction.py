"""Sprint 1.8 conservation invariants and regression tests."""
import tempfile
import unittest
from pathlib import Path

from app.solver.core import Availability, EngineeringValue
from app.solver.sequential_extraction import ConservationEvaluator, ExtractionInput, ExtractionStateAdapter, SequentialExtractionEvaluator
from app.solver.state import SegmentState
from app.verification.extraction_runner import POLICY, available, canonical_extraction_cases, instruction, result_payload, run


class SequentialExtractionTests(unittest.TestCase):
    def test_canonical_contracts(self):
        for case in canonical_extraction_cases():
            payload=result_payload(case)
            self.assertEqual(payload["completed"],case.expected_completed,case.case_id)

    def test_local_and_global_conservation_success(self):
        result=SequentialExtractionEvaluator().evaluate(canonical_extraction_cases()[1].inputs,POLICY)
        self.assertTrue(result.completed)
        self.assertTrue(all(item.residual.conserved for item in result.accepted))
        self.assertTrue(result.global_residual.conserved)
        self.assertEqual(result.terminal_downstream.value,4)

    def test_local_conservation_failure_is_explicit(self):
        residual=ConservationEvaluator().evaluate(available(10),available(2),available(7),POLICY)
        self.assertFalse(residual.conserved)
        self.assertEqual(residual.residual.value,1)

    def test_global_conservation_failure_uses_same_contract(self):
        residual=ConservationEvaluator().evaluate(available(10),available(6),available(5),POLICY)
        self.assertFalse(residual.conserved)

    def test_unavailable_residual_never_conserves(self):
        residual=ConservationEvaluator().evaluate(EngineeringValue.unavailable("missing",POLICY.unit),available(1),available(1),POLICY)
        self.assertIsNone(residual.conserved); self.assertIsNone(residual.residual.value)

    def test_zero_is_available_and_distinct_from_unavailable(self):
        zero=available(0); missing=EngineeringValue.unavailable("missing",POLICY.unit)
        self.assertEqual(zero.availability,Availability.AVAILABLE); self.assertEqual(zero.value,0); self.assertIsNone(missing.value)

    def test_failed_middle_preserves_only_previous_accepted_state(self):
        case=next(item for item in canonical_extraction_cases() if item.case_id=="failed-middle-isolation")
        result=SequentialExtractionEvaluator().evaluate(case.inputs,POLICY)
        self.assertFalse(result.completed); self.assertEqual(tuple(item.outlet_id for item in result.accepted),("O1",)); self.assertIsNone(result.terminal_downstream.value)

    def test_adapter_preserves_passed_through_identity(self):
        pressure=EngineeringValue.unavailable("not modeled"); momentum=EngineeringValue.unavailable("not modeled")
        incoming=SegmentState("in",available(10),pressure,momentum)
        output=ExtractionStateAdapter(instruction("O1",available(2)),POLICY).evaluate(incoming,"O1")
        self.assertIs(output.incoming,incoming); self.assertIs(output.outgoing.pressure,pressure); self.assertIs(output.outgoing.momentum_direction,momentum)

    def test_deterministic_serialization_payload(self):
        case=canonical_extraction_cases()[0]; self.assertEqual(result_payload(case),result_payload(case))

    def test_no_forbidden_quantities_or_recommendation(self):
        payload=result_payload(canonical_extraction_cases()[0]); self.assertTrue(all(value is None for value in payload["excluded_quantities"].values())); self.assertIsNone(payload["recommendation"])

    def test_corrupted_conservation_golden_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory); run(path,update=True,confirmed=True)
            golden=path/"one-prescribed-outlet.json"; golden.write_text(golden.read_text(encoding="utf-8").replace('"completed": true','"completed": false'),encoding="utf-8")
            self.assertNotEqual(run(path),0)


if __name__=="__main__": unittest.main()
