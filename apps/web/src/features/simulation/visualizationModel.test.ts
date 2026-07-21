import { describe, expect, it } from "vitest";
import type { SimulationResult } from "../../api/contracts";
import { INITIAL_FORM } from "./initialState";
import { buildEngineeringSceneModel,buildParticleIndicators,particleControlPoint,solverToSceneVector } from "./visualizationModel";

const engineeringValue = (value: number, unit: string) => ({ availability: "available" as const, value, unit, unavailable_reason: null, provenance: null });
const result = {
  rows: 2,
  columns: 4,
  outlets: Array.from({ length: 8 }, (_, index) => ({
    outlet_id: `R${Math.floor(index / 4)}C${index % 4}`,
    row: Math.floor(index / 4),
    column: index % 4,
    airflow_percentage: engineeringValue(8 + index, "%"),
    airflow_cfm: engineeringValue(64 + index * 8, "CFM"),
    airflow_cmh: engineeringValue(108 + index * 14, "m^3/h"),
    outlet_velocity_mps: engineeringValue(1 + index / 10, "m/s"),
  })),
} as SimulationResult;

describe("engineering visualization projection", () => {
  it("maps geometry without requiring solver output", () => {
    const model = buildEngineeringSceneModel(INITIAL_FORM, null, "airflow_percentage");
    expect(model.outlets).toHaveLength(8);
    expect(model.deflectors).toHaveLength(1);
    expect(model.hasSolverResult).toBe(false);
    expect(model.outlets.every(outlet => outlet.value === null && outlet.heat === null)).toBe(true);
  });

  it("preserves solver values and only normalizes their visual heat", () => {
    const model = buildEngineeringSceneModel(INITIAL_FORM, result, "airflow_cfm");
    expect(model.outlets.map(outlet => outlet.value?.value)).toEqual(result.outlets.map(outlet => outlet.airflow_cfm.value));
    expect(model.outlets[0].heat).toBe(0);
    expect(model.outlets[7].heat).toBe(1);
  });

  it("maps multiple deflectors directly from form geometry", () => {
    const second = { ...INITIAL_FORM.deflectors[0], identifier: "D2", position_m: { x: 0.4, y: 0.1, z: 0.6 }, angle_deg_about_y: 30 };
    const form = { ...INITIAL_FORM, deflectors: [...INITIAL_FORM.deflectors, second] };
    const model = buildEngineeringSceneModel(form, null, "airflow_percentage");
    expect(model.deflectors).toEqual(form.deflectors);
  });

  it("normalizes inlet direction and preserves its configured origin",()=>{
    const form={...INITIAL_FORM,inlet:{position:{x:.2,y:-.1,z:1.7},direction:{x:1,y:2,z:-2}}};
    const model=buildEngineeringSceneModel(form,null,"airflow_percentage");
    expect(model.inlet.position).toEqual([.2,-.1,1.7]);
    expect(model.inlet.direction).toEqual([1/3,2/3,-2/3]);
  });

  it("maps all canonical solver directions to the same arrow and initial particle tangent",()=>{
    const directions:[[number,number,number],string][]=[[[0,0,-1],"down"],[[0,0,1],"up"],[[1,0,0],"left-to-right"],[[-1,0,0],"right-to-left"],[[0,1,0],"front-to-back"],[[0,-1,0],"back-to-front"],[[1/3,2/3,-2/3],"diagonal"]];
    for(const [solverDirection] of directions){const sceneDirection=solverToSceneVector(solverDirection);const start:[number,number,number]=[0,2,0];const control=particleControlPoint(start,sceneDirection,2);const tangent=control.map((value,index)=>(value-start[index])/.6);expect(tangent[0]).toBeCloseTo(sceneDirection[0]);expect(tangent[1]).toBeCloseTo(sceneDirection[1]);expect(tangent[2]).toBeCloseTo(sceneDirection[2])}
  });

  it("creates independent fan emitters only for enabled solver-backed fans",()=>{
    const fanValue=(value:number,unit:string)=>engineeringValue(value,unit);
    const fan=(equipment_id:"SF-501"|"SF-502",enabled:boolean,airflow:number)=>({equipment_id,enabled,status:enabled?"RUNNING":"OFF",frequency_hz:fanValue(enabled?60:0,"Hz"),motor_power_hp:fanValue(100,"HP"),rated_airflow_cmh:fanValue(110000,"m^3/h"),rated_static_pressure_pa:fanValue(1600,"Pa"),maximum_frequency_hz:fanValue(60,"Hz"),current_airflow_cmh:fanValue(airflow,"m^3/h"),current_airflow_cfm:fanValue(airflow/1.69901082,"CFM"),current_static_pressure_pa:fanValue(enabled?1600:0,"Pa"),inlet_velocity_mps:fanValue(enabled?190.97:0,"m/s"),estimation_label:"Estimated using Fan Affinity Laws"});
    const withFans={...result,fan_operating_results:[fan("SF-501",true,110000),fan("SF-502",false,0)]} as SimulationResult;
    const one=buildParticleIndicators(buildEngineeringSceneModel(INITIAL_FORM,withFans,"airflow_percentage")).filter(item=>item.kind==="fan-emitter");
    expect(one.map(item=>item.id)).toEqual(["SF-501"]);expect(one[0].count).toBe(10);
    const both={...result,fan_operating_results:[fan("SF-501",true,110000),fan("SF-502",true,55000)]} as SimulationResult;
    const two=buildParticleIndicators(buildEngineeringSceneModel(INITIAL_FORM,both,"airflow_percentage")).filter(item=>item.kind==="fan-emitter");
    expect(two.map(item=>item.id)).toEqual(["SF-501","SF-502"]);expect(two[1].count).toBe(5);expect(two[0].direction).toEqual(two[1].direction);
  });
});
