import type { EngineeringValue, FanOperatingResult,SimulationResult } from "../../api/contracts";
import type { WorkspaceForm } from "./initialState";

export type HeatMetric = "airflow_percentage" | "airflow_cfm" | "airflow_cmh" | "outlet_velocity_mps";

export interface OutletVisual {
  id: string;
  row: number;
  column: number;
  position: [number, number, number];
  width: number;
  height: number;
  value: EngineeringValue | null;
  airflowPercentage:number|null;
  airflowCmh:number|null;
  velocityMps:number|null;
  heat: number | null;
}

export interface EngineeringSceneModel {
  plenum: { width: number; height: number; depth: number };
  inlet: { width: number; height: number; position: [number, number, number]; direction: [number, number, number] };
  outlets: OutletVisual[];
  deflectors: WorkspaceForm["deflectors"];
  fanEmitters: FanOperatingResult[];
  hasSolverResult: boolean;
}
export interface ParticleIndicator {id:string;kind:"fan-emitter"|"outlet";start:[number,number,number];direction:[number,number,number];count:number;engineeringSpeed:number;color:string}

export function solverToSceneVector(value:readonly [number,number,number]|{x:number;y:number;z:number}):[number,number,number]{
  if(Array.isArray(value))return [value[0],value[2],value[1]];
  const vector=value as {x:number;y:number;z:number};return [vector.x,vector.z,vector.y];
}

export function particleControlPoint(start:[number,number,number],direction:[number,number,number],extent:number):[number,number,number]{return [start[0]+direction[0]*extent*0.3,start[1]+direction[1]*extent*0.3,start[2]+direction[2]*extent*0.3]}

export function buildParticleIndicators(model:EngineeringSceneModel):ParticleIndicator[]{
  const inletStart=solverToSceneVector(model.inlet.position),inletDirection=solverToSceneVector(model.inlet.direction);
  const fans=model.fanEmitters.filter(fan=>fan.enabled&&fan.current_airflow_cmh.value!==null).map((fan,index)=>({id:fan.equipment_id,kind:"fan-emitter" as const,start:inletStart,direction:inletDirection,count:Math.max(0,Math.round(((fan.current_airflow_cmh.value??0)/(fan.rated_airflow_cmh.value??110000))*10)),engineeringSpeed:fan.inlet_velocity_mps.value??0,color:index===0?"#6dd9cf":"#d8ff4f"}));
  const outlets=model.outlets.filter(outlet=>outlet.airflowCmh!==null&&outlet.velocityMps!==null).map(outlet=>({id:outlet.id,kind:"outlet" as const,start:solverToSceneVector(outlet.position),direction:[0,-1,0] as [number,number,number],count:Math.max(0,Math.round((outlet.airflowCmh??0)/220000*80)),engineeringSpeed:outlet.velocityMps??0,color:"#d8ff4f"}));
  return [...fans,...outlets];
}

export function buildEngineeringSceneModel(form: WorkspaceForm, result: SimulationResult | null, metric: HeatMetric): EngineeringSceneModel {
  const width = form.grille_width_mm / 1000;
  const height = form.grille_height_mm / 1000;
  const depth = form.plenum_depth_mm / 1000;
  const outletWidth = form.outlet_width_mm / 1000;
  const outletHeight = form.outlet_height_mm / 1000;
  const resultByCell = new Map(result?.outlets.map(outlet => [`${outlet.row}:${outlet.column}`, outlet]) ?? []);
  const available = result?.outlets
    .map(outlet => outlet[metric].value)
    .filter((value): value is number => value !== null) ?? [];
  const minimum = available.length ? Math.min(...available) : 0;
  const maximum = available.length ? Math.max(...available) : 0;
  const outlets: OutletVisual[] = [];

  for (let row = 0; row < form.rows; row += 1) {
    for (let column = 0; column < form.columns; column += 1) {
      const resultOutlet = resultByCell.get(`${row}:${column}`);
      const value = resultOutlet?.[metric] ?? null;
      const numeric = value?.value ?? null;
      outlets.push({
        id: resultOutlet?.outlet_id ?? `R${row}C${column}`,
        row,
        column,
        position: [((column + 0.5) / form.columns - 0.5) * width, (0.5 - (row + 0.5) / form.rows) * height, 0],
        width: outletWidth,
        height: outletHeight,
        value,
        airflowPercentage:resultOutlet?.airflow_percentage.value??null,
        airflowCmh:resultOutlet?.airflow_cmh.value??null,
        velocityMps:resultOutlet?.outlet_velocity_mps.value??null,
        heat: numeric === null ? null : maximum === minimum ? 0.5 : (numeric - minimum) / (maximum - minimum),
      });
    }
  }

  const directionMagnitude=Math.hypot(form.inlet.direction.x,form.inlet.direction.y,form.inlet.direction.z);
  const direction:[number,number,number]=directionMagnitude===0?[0,0,0]:[form.inlet.direction.x/directionMagnitude,form.inlet.direction.y/directionMagnitude,form.inlet.direction.z/directionMagnitude];
  return {
    plenum: { width, height, depth },
    inlet: { width: form.inlet_width_mm / 1000, height: form.inlet_height_mm / 1000, position: [form.inlet.position.x,form.inlet.position.y,form.inlet.position.z], direction },
    outlets,
    deflectors: form.deflectors,
    fanEmitters: result?.fan_operating_results ?? [],
    hasSolverResult: result !== null,
  };
}
