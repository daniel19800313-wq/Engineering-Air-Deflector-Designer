"""Sprint 2.0 experimental model and conservation tests."""
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from app.solver.airflow_solver import CFM_TO_CMH, DirectionalAreaDistanceKernel, ExperimentalAirflowSolver, ProjectedAreaReflectionInfluence
from app.solver.core import Availability
from app.verification.airflow_runner import POLICY,base_input,canonical_airflow_cases,result_payload,run


class ExperimentalAirflowSolverTests(unittest.TestCase):
    def setUp(self):self.solver=ExperimentalAirflowSolver(DirectionalAreaDistanceKernel(),ProjectedAreaReflectionInfluence())

    def test_reads_eight_outlets_and_conserves_supplied_total(self):
        result=self.solver.solve(base_input(),POLICY)
        self.assertTrue(result.completed);self.assertEqual(len(result.outlets),8);self.assertTrue(result.conserved)
        self.assertAlmostEqual(sum(item.estimated_airflow_cfm.value for item in result.outlets),800)
        self.assertAlmostEqual(sum(item.percentage.value for item in result.outlets),100)

    def test_deflector_angle_changes_distribution(self):
        positive=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="single-deflector-positive-angle"));negative=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="single-deflector-negative-angle"))
        self.assertNotEqual([x["percentage"] for x in positive["outlets"]],[x["percentage"] for x in negative["outlets"]])

    def test_deflector_position_changes_distribution(self):
        base=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="single-deflector-positive-angle"));shifted=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="deflector-position-shift"))
        self.assertNotEqual([x["percentage"] for x in base["outlets"]],[x["percentage"] for x in shifted["outlets"]])

    def test_multiple_deflectors_supported_and_conserved(self):
        payload=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="multiple-deflectors"));self.assertTrue(payload["completed"]);self.assertTrue(payload["conserved"]);self.assertEqual(len(payload["deflectors"]),2)

    def test_invalid_direction_rejected_without_results(self):
        payload=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="invalid-inlet-direction"));self.assertFalse(payload["completed"]);self.assertEqual(payload["outlets"],[]);self.assertIsNone(payload["recommendation"])

    def test_deterministic_contract(self):
        case=next(item for item in canonical_airflow_cases() if item.case_id=="single-deflector-positive-angle");self.assertEqual(result_payload(case),result_payload(case))

    def test_claim_and_provenance_remain_experimental(self):
        payload=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="single-deflector-positive-angle"));self.assertEqual(payload["claim_label"],"experimental_scaled_distribution");self.assertTrue(all(item["provenance"]=="documented_v0.1_proxy" for item in payload["outlets"]));self.assertEqual(payload["validation"],"experimental_not_validated_hvac_physics")

    def test_empty_deflector_collection_is_valid_baseline(self):
        payload=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="no-deflector-baseline"));self.assertTrue(payload["completed"]);self.assertEqual(payload["deflectors"],[]);self.assertTrue(payload["conserved"])

    def test_sixty_degree_case_completes(self):
        payload=result_payload(next(item for item in canonical_airflow_cases() if item.case_id=="single-deflector-60-degrees"));self.assertTrue(payload["completed"]);self.assertTrue(payload["conserved"])

    def test_no_sequential_extraction_exceeds_remaining(self):
        for case in canonical_airflow_cases():
            payload=result_payload(case)
            if not payload["completed"]: continue
            remaining=payload["supplied_total_cfm"]
            for outlet in payload["outlets"]:
                self.assertLessEqual(outlet["estimated_airflow_cfm"],remaining)
                remaining=remaining-outlet["estimated_airflow_cfm"]
            self.assertAlmostEqual(remaining,0)

    def test_corrupted_airflow_golden_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);run(target,update=True,confirmed=True)
            path=target/"single-deflector-positive-angle.json";path.write_text(path.read_text(encoding="utf-8").replace('"completed": true','"completed": false'),encoding="utf-8")
            self.assertNotEqual(run(target),0)

    def test_unit_outputs_preserve_existing_percentage_and_cfm(self):
        baseline=self.solver.solve(base_input(),POLICY)
        with_geometry=replace(base_input(),outlets=tuple(replace(item,free_area_ratio=0.75) for item in base_input().outlets))
        enriched=self.solver.solve(with_geometry,POLICY)
        self.assertEqual([item.percentage.value for item in baseline.outlets],[item.percentage.value for item in enriched.outlets])
        self.assertEqual([item.estimated_airflow_cfm.value for item in baseline.outlets],[item.estimated_airflow_cfm.value for item in enriched.outlets])

    def test_cmh_conversion_and_total_are_correct(self):
        result=self.solver.solve(base_input(),POLICY)
        for item in result.outlets:
            self.assertAlmostEqual(item.airflow_cmh.value,item.airflow_cfm.value*CFM_TO_CMH)
        self.assertAlmostEqual(sum(item.airflow_cmh.value for item in result.outlets),800*CFM_TO_CMH)

    def test_velocity_calculation_and_provenance_with_valid_geometry(self):
        data=replace(base_input(),outlets=tuple(replace(item,free_area_ratio=0.5) for item in base_input().outlets))
        result=self.solver.solve(data,POLICY); item=result.outlets[0]
        expected=(item.airflow_cfm.value*CFM_TO_CMH/3600)/((300/1000)*(300/1000)*0.5)
        self.assertAlmostEqual(item.outlet_velocity_mps.value,expected)
        self.assertEqual(item.calculation_provenance.geometric_outlet_area_m2.value,0.09)
        self.assertEqual(item.calculation_provenance.free_area_ratio.value,0.5)
        self.assertEqual(item.calculation_provenance.effective_outlet_area_m2.value,0.045)
        self.assertEqual(item.calculation_provenance.total_inlet_airflow_cfm.value,800)
        self.assertEqual(item.calculation_provenance.cfm_to_cmh_conversion.value,CFM_TO_CMH)

    def test_missing_or_invalid_velocity_geometry_is_explicitly_unavailable(self):
        variants=(
            (replace(base_input().outlets[0],width_mm=None),"OUTLET_VELOCITY_WIDTH_MM_UNAVAILABLE"),
            (replace(base_input().outlets[0],height_mm=None),"OUTLET_VELOCITY_HEIGHT_MM_UNAVAILABLE"),
            (replace(base_input().outlets[0],free_area_ratio=None),"OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE"),
            (replace(base_input().outlets[0],width_mm=-1),"OUTLET_VELOCITY_WIDTH_MM_INVALID"),
            (replace(base_input().outlets[0],height_mm=-1),"OUTLET_VELOCITY_HEIGHT_MM_INVALID"),
            (replace(base_input().outlets[0],free_area_ratio=0),"OUTLET_VELOCITY_FREE_AREA_RATIO_INVALID"),
        )
        for changed,reason in variants:
            with self.subTest(reason=reason):
                data=replace(base_input(),outlets=(changed,)+base_input().outlets[1:])
                result=self.solver.solve(data,POLICY); item=result.outlets[0]
                self.assertTrue(result.completed)
                self.assertEqual(item.outlet_velocity_mps.availability,Availability.UNAVAILABLE)
                self.assertEqual(item.outlet_velocity_mps.unavailable_reason,reason)
                self.assertEqual(item.airflow_cmh.availability,Availability.AVAILABLE)

    def test_free_area_ratio_one_is_accepted(self):
        data=replace(base_input(),outlets=tuple(replace(item,free_area_ratio=1.0) for item in base_input().outlets))
        result=self.solver.solve(data,POLICY)
        self.assertTrue(all(item.outlet_velocity_mps.availability==Availability.AVAILABLE for item in result.outlets))

    def test_total_cfm_conservation_is_unchanged_with_velocity_geometry(self):
        data=replace(base_input(),outlets=tuple(replace(item,free_area_ratio=0.5) for item in base_input().outlets))
        result=self.solver.solve(data,POLICY)
        self.assertTrue(result.conserved)
        self.assertAlmostEqual(sum(item.airflow_cfm.value for item in result.outlets),800)


if __name__=="__main__":unittest.main()
