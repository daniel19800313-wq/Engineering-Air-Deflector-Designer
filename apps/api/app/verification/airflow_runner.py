"""Golden runner for the experimental airflow prototype contracts."""
from __future__ import annotations
import argparse
from dataclasses import dataclass, replace
from pathlib import Path

from app.solver.airflow_solver import AirflowDeflector, AirflowInlet, AirflowOutlet, AirflowPlenum, DirectionalAreaDistanceKernel, ExperimentalAirflowInput, ExperimentalAirflowPolicy, ExperimentalAirflowSolver, ProjectedAreaReflectionInfluence
from app.solver.core import Provenance
from app.solver.geometry import Vector3
from .golden import compare_golden, update_golden


POLICY=ExperimentalAirflowPolicy(0.000001,0.000001,Provenance("verification_policy","sprint-2.0-explicit-tolerance"),"experimental-airflow-v0.1")


def base_input()->ExperimentalAirflowInput:
    outlets=tuple(AirflowOutlet(f"R{r}C{c}",Vector3(-1.5+c, -0.4+0.8*r,0),0.3,0.3,r*4+c,width_mm=300.0,height_mm=300.0,free_area_ratio=None) for r in range(2) for c in range(4))
    return ExperimentalAirflowInput(AirflowPlenum(4,2,2),AirflowInlet(Vector3(0,0,2),0.4,0.4,Vector3(0,0,-1),800),outlets,(AirflowDeflector("D1",Vector3(0,0,1),45,0.2,0.2),))


@dataclass(frozen=True,slots=True)
class AirflowCase:
    case_id:str
    data:ExperimentalAirflowInput
    expected_completed:bool


def canonical_airflow_cases()->tuple[AirflowCase,...]:
    base=base_input()
    return (
        AirflowCase("no-deflector-baseline",replace(base,deflectors=()),True),
        AirflowCase("single-deflector-30-degrees",replace(base,deflectors=(replace(base.deflectors[0],angle_deg_about_y=30),)),True),
        AirflowCase("single-deflector-positive-angle",base,True),
        AirflowCase("single-deflector-60-degrees",replace(base,deflectors=(replace(base.deflectors[0],angle_deg_about_y=60),)),True),
        AirflowCase("single-deflector-negative-angle",replace(base,deflectors=(replace(base.deflectors[0],angle_deg_about_y=-45),)),True),
        AirflowCase("parallel-zero-projection",replace(base,deflectors=(replace(base.deflectors[0],angle_deg_about_y=90),)),True),
        AirflowCase("deflector-position-shift",replace(base,deflectors=(replace(base.deflectors[0],center_m=Vector3(0.5,0,1)),)),True),
        AirflowCase("multiple-deflectors",replace(base,deflectors=(base.deflectors[0],AirflowDeflector("D2",Vector3(0.5,0,0.8),-45,0.15,0.2))),True),
        AirflowCase("invalid-inlet-direction",replace(base,inlet=replace(base.inlet,direction=Vector3(0,0,-2))),False),
    )


def result_payload(case:AirflowCase)->dict[str,object]:
    result=ExperimentalAirflowSolver(DirectionalAreaDistanceKernel(),ProjectedAreaReflectionInfluence()).solve(case.data,POLICY)
    return {"case_id":case.case_id,"completed":result.completed,"claim_label":result.claim_label,"outlets":[{"outlet_id":item.outlet_id,"downstream_order":item.downstream_order,"estimated_airflow_cfm":item.estimated_airflow_cfm.value,"percentage":item.percentage.value,"provenance":item.estimated_airflow_cfm.provenance.model_relationship if item.estimated_airflow_cfm.provenance else None} for item in result.outlets],"supplied_total_cfm":result.supplied_total_cfm.value,"estimated_total_cfm":result.estimated_total_cfm.value,"terminal_remaining_cfm":result.terminal_remaining_cfm.value,"conservation_residual_cfm":result.conservation_residual_cfm.value,"conserved":result.conserved,"deflectors":[{"id":item.deflector_id,"normal":{"x":item.normal.x,"y":item.normal.y,"z":item.normal.z},"projected_area_m2":item.projected_area_m2,"intercepted_fraction_proxy":item.intercepted_fraction_proxy,"redirected_weights_usable":item.redirected_weights_usable} for item in result.deflector_audit],"assumptions":list(result.assumptions),"diagnostics":list(result.diagnostics),"recommendation":result.recommendation,"validation":"experimental_not_validated_hvac_physics"}


def run(golden_dir:Path,*,update:bool=False,confirmed:bool=False)->int:
    failed=0
    for case in canonical_airflow_cases():
        payload=result_payload(case); failures=[]
        if payload["completed"] is not case.expected_completed: failures.append("completion mismatch")
        path=golden_dir/f"{case.case_id}.json"
        if update:update_golden(path,payload,confirmed=confirmed)
        else:
            matches,diff=compare_golden(path,payload)
            if not matches:failures.append("golden mismatch\n"+diff)
        if failures:
            failed+=1;print(f"FAIL {case.case_id} [experimental model regression]")
            for item in failures:print(f"  {item}")
        else:print(f"PASS {case.case_id}")
    print(f"SUMMARY pass={len(canonical_airflow_cases())-failed} fail={failed}");return 1 if failed else 0


def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument("--goldens",type=Path,default=Path("verification/airflow_goldens"));parser.add_argument("--update-golden",action="store_true");parser.add_argument("--confirm-update",action="store_true");args=parser.parse_args()
    if args.confirm_update and not args.update_golden:parser.error("--confirm-update requires --update-golden")
    return run(args.goldens,update=args.update_golden,confirmed=args.confirm_update)


if __name__=="__main__":raise SystemExit(main())
