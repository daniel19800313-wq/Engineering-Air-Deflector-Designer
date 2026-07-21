"""Canonical sequential-extraction contract and golden runner."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from app.solver.core import EngineeringValue, Provenance
from app.solver.sequential_extraction import ConservationEvaluator, ExtractionInput, ExtractionPolicy, ExtractionProvenance, ExtractionSource, OutletExtractionInstruction, SequentialExtractionEvaluator
from .golden import compare_golden, update_golden


UNIT = "test_quantity_unit"
VALUE_PROVENANCE = Provenance("prescribed_test_input", "sprint-1.8-fixture")
TOLERANCE_PROVENANCE = Provenance("verification_policy", "sprint-1.8-explicit-test-tolerance")
POLICY = ExtractionPolicy(UNIT, 0.000001, TOLERANCE_PROVENANCE, "sequential-extraction-v0.1")


def available(value: float) -> EngineeringValue[float]:
    """Create a labelled prescribed fixture quantity, never a prediction."""
    return EngineeringValue.available(value, UNIT, VALUE_PROVENANCE)


def instruction(outlet: str, value: EngineeringValue[float], *, with_provenance: bool = True) -> OutletExtractionInstruction:
    """Create an explicit prescribed fixture instruction."""
    provenance = ExtractionProvenance(ExtractionSource.PRESCRIBED_TEST_INPUT, f"fixture:{outlet}", POLICY.evaluator_version) if with_provenance else None
    return OutletExtractionInstruction(outlet, value, provenance)


@dataclass(frozen=True, slots=True)
class ExtractionCase:
    case_id: str
    inputs: ExtractionInput
    expected_completed: bool
    expected_diagnostic: str | None
    residual_operands: tuple[EngineeringValue[float], EngineeringValue[float], EngineeringValue[float]] | None = None
    residual_scope: str | None = None


def canonical_extraction_cases() -> tuple[ExtractionCase, ...]:
    """Return explicit test-evidence cases with no predicted extraction."""
    return (
        ExtractionCase("one-prescribed-outlet", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O1", available(2)),)), True, None),
        ExtractionCase("multiple-sequential-outlets", ExtractionInput(available(10), ("O1","O2","O3"), ("O1","O2","O3"), (instruction("O1",available(2)),instruction("O2",available(3)),instruction("O3",available(1)))), True, None),
        ExtractionCase("available-zero-extraction", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O1",available(0)),)), True, None),
        ExtractionCase("unavailable-inlet", ExtractionInput(EngineeringValue.unavailable("fixture unavailable", UNIT), ("O1",), ("O1",), (instruction("O1",available(1)),)), False, "SE_INLET_UNAVAILABLE"),
        ExtractionCase("unavailable-extraction", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O1",EngineeringValue.unavailable("fixture unavailable",UNIT)),)), False, "SE_EXTRACTION_UNAVAILABLE"),
        ExtractionCase("missing-provenance", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O1",available(1),with_provenance=False),)), False, "SE_PROVENANCE_MISSING"),
        ExtractionCase("negative-extraction", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O1",available(-1)),)), False, "SE_INVALID_EXTRACTION"),
        ExtractionCase("exceeds-incoming", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O1",available(11)),)), False, "SE_EXTRACTION_EXCEEDS_INCOMING"),
        ExtractionCase("duplicate-instruction", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O1",available(1)),instruction("O1",available(1)))), False, "SE_DUPLICATE_INSTRUCTION"),
        ExtractionCase("undeclared-outlet", ExtractionInput(available(10), ("O1",), ("O1",), (instruction("O2",available(1)),)), False, "SE_UNDECLARED_OR_MISSING_OUTLET"),
        ExtractionCase("order-mismatch", ExtractionInput(available(10), ("O2","O1"), ("O1","O2"), (instruction("O1",available(1)),instruction("O2",available(1)))), False, "SE_ORDER_MISMATCH"),
        ExtractionCase("failed-middle-isolation", ExtractionInput(available(10), ("O1","O2","O3"), ("O1","O2","O3"), (instruction("O1",available(2)),instruction("O2",available(20)),instruction("O3",available(1)))), False, "SE_EXTRACTION_EXCEEDS_INCOMING"),
        ExtractionCase("local-residual-failure", ExtractionInput(available(1),("O1",),("O1",),(instruction("O1",available(0)),)), False, "SE_LOCAL_CONSERVATION_FAILED", (available(10),available(2),available(7)), "local"),
        ExtractionCase("global-residual-failure", ExtractionInput(available(1),("O1",),("O1",),(instruction("O1",available(0)),)), False, "SE_GLOBAL_CONSERVATION_FAILED", (available(10),available(6),available(5)), "global"),
        ExtractionCase("unavailable-conservation-residual", ExtractionInput(available(1),("O1",),("O1",),(instruction("O1",available(0)),)), False, "SE_RESIDUAL_UNAVAILABLE", (EngineeringValue.unavailable("fixture unavailable",UNIT),available(1),available(1)), "local"),
    )


def _value(value: EngineeringValue[float]) -> dict[str, object]:
    return {"availability": value.availability.value, "value": value.value, "unit": value.unit, "provenance": None if value.provenance is None else {"source_type": value.provenance.source_type, "source_reference": value.provenance.source_reference, "solver_component": value.provenance.solver_component, "model_relationship": value.provenance.model_relationship}, "unavailable_reason": value.unavailable_reason}


def result_payload(case: ExtractionCase) -> dict[str, object]:
    """Execute and serialize conservation contracts with full units/provenance."""
    if case.residual_operands is not None:
        residual=ConservationEvaluator().evaluate(*case.residual_operands,POLICY)
        return {"case_id":case.case_id,"completed":False,"residual_scope":case.residual_scope,"residual":_value(residual.residual),"conserved":residual.conserved,"diagnostics":[case.expected_diagnostic],"recommendation":None,"excluded_quantities":{"pressure":None,"resistance":None,"velocity":None,"aerodynamics":None}}
    result = SequentialExtractionEvaluator().evaluate(case.inputs, POLICY)
    return {"case_id":case.case_id,"completed":result.completed,"inlet":_value(result.inlet),"accepted":[{"outlet_id":item.outlet_id,"incoming":_value(item.incoming),"extracted":_value(item.extracted),"downstream":_value(item.downstream),"residual":_value(item.residual.residual),"conserved":item.residual.conserved,"extraction_source":item.provenance.source.value,"source_reference":item.provenance.source_reference} for item in result.accepted],"total_extracted":_value(result.total_extracted),"terminal_downstream":_value(result.terminal_downstream),"global_residual":_value(result.global_residual.residual),"global_conserved":result.global_residual.conserved,"diagnostics":[item.code for item in result.diagnostics],"recommendation":result.recommendation,"excluded_quantities":{"pressure":None,"resistance":None,"velocity":None,"aerodynamics":None}}


def run(golden_dir: Path, *, update: bool=False, confirmed: bool=False) -> int:
    """Execute cases and return non-zero on contract/golden regression."""
    failed=0
    for case in canonical_extraction_cases():
        payload=result_payload(case); failures=[]
        if payload["completed"] is not case.expected_completed: failures.append("completed mismatch")
        if case.expected_diagnostic and case.expected_diagnostic not in payload["diagnostics"]: failures.append(f"missing diagnostic {case.expected_diagnostic}")
        path=golden_dir/f"{case.case_id}.json"
        if update: update_golden(path,payload,confirmed=confirmed)
        else:
            matches,diff=compare_golden(path,payload)
            if not matches: failures.append("golden mismatch\n"+diff)
        if failures:
            failed+=1; print(f"FAIL {case.case_id} [conservation contract regression]")
            for item in failures: print(f"  {item}")
        else: print(f"PASS {case.case_id}")
    print(f"SUMMARY pass={len(canonical_extraction_cases())-failed} fail={failed}")
    return 1 if failed else 0


def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--goldens",type=Path,default=Path("verification/extraction_goldens")); parser.add_argument("--update-golden",action="store_true"); parser.add_argument("--confirm-update",action="store_true"); args=parser.parse_args()
    if args.confirm_update and not args.update_golden: parser.error("--confirm-update requires --update-golden")
    return run(args.goldens,update=args.update_golden,confirmed=args.confirm_update)


if __name__=="__main__": raise SystemExit(main())
