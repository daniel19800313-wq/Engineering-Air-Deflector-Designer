import type {
  EngineeringValue,
  FanOperatingResult,
  SimulationResult,
} from "../../api/contracts";
import type { WorkspaceForm } from "./initialState";

export type HeatMetric =
  | "airflow_percentage"
  | "airflow_cfm"
  | "airflow_cmh"
  | "outlet_velocity_mps";

export type FlowSegmentKind = "duct" | "outlet";

export interface OutletVisual {
  id: string;
  row: number;
  column: number;
  position: [number, number, number];
  width: number;
  height: number;
  value: EngineeringValue | null;
  airflowPercentage: number | null;
  airflowCmh: number | null;
  velocityMps: number | null;
  heat: number | null;
}

/**
 * Visual-only duct geometry.
 *
 * The current form does not contain an engineering duct length input.
 * Therefore, length is an explicitly identified visualization estimate and
 * must not be interpreted as a solver-derived physical dimension.
 */
export interface DuctVisual {
  width: number;
  height: number;
  length: number;
  endPosition: [number, number, number];
  direction: [number, number, number];
  estimatedLength: true;
}

export interface EngineeringSceneModel {
  plenum: {
    width: number;
    height: number;
    depth: number;
  };

  inlet: {
    width: number;
    height: number;
    position: [number, number, number];
    direction: [number, number, number];
  };

  ductVisual: DuctVisual;
  outlets: OutletVisual[];
  deflectors: WorkspaceForm["deflectors"];
  fanEmitters: FanOperatingResult[];
  hasSolverResult: boolean;
}

/**
 * A solver-backed straight flow section used by the Engineering
 * Visualization Engine.
 *
 * This model describes only values supported by solver output:
 *
 * - Duct segments use individual fan operating results.
 * - Outlet segments use individual outlet airflow and velocity results.
 *
 * It does not invent plenum streamlines, turbulence, collisions, or CFD paths.
 */
export interface FlowSegment {
  id: string;
  kind: FlowSegmentKind;
  sourceId: string;
  start: [number, number, number];
  direction: [number, number, number];
  length: number;
  count: number;
  engineeringSpeed: number;
  engineeringAirflowCmh: number;
  color: string;
}

/**
 * Converts solver coordinates into Three.js scene coordinates.
 *
 * Solver: [x, y, z]
 * Scene : [x, z, y]
 */
export function solverToSceneVector(
  value:
    | readonly [number, number, number]
    | { x: number; y: number; z: number },
): [number, number, number] {
  if (Array.isArray(value)) {
    return [value[0], value[2], value[1]];
  }

  const vector = value as { x: number; y: number; z: number };

  return [vector.x, vector.z, vector.y];
}

export function particleControlPoint(
  start: [number, number, number],
  direction: [number, number, number],
  extent: number,
): [number, number, number] {
  return [
    start[0] + direction[0] * extent * 0.3,
    start[1] + direction[1] * extent * 0.3,
    start[2] + direction[2] * extent * 0.3,
  ];
}

function normalizeVector(
  vector: [number, number, number],
): [number, number, number] {
  const magnitude = Math.hypot(vector[0], vector[1], vector[2]);

  if (magnitude === 0) {
    return [0, 0, 0];
  }

  return [
    vector[0] / magnitude,
    vector[1] / magnitude,
    vector[2] / magnitude,
  ];
}

/**
 * Returns a perpendicular offset used only to keep the two independent fan
 * emitters visually distinguishable when they share the same duct path.
 *
 * It does not represent a calculated airflow separation.
 */
function buildEmitterOffset(
  direction: [number, number, number],
  index: number,
  emitterCount: number,
  inletWidth: number,
): [number, number, number] {
  if (emitterCount <= 1) {
    return [0, 0, 0];
  }

  const directionVector = normalizeVector(direction);

  let reference: [number, number, number] = [0, 1, 0];

  if (Math.abs(directionVector[1]) > 0.9) {
    reference = [1, 0, 0];
  }

  const perpendicular: [number, number, number] = normalizeVector([
    directionVector[1] * reference[2] -
      directionVector[2] * reference[1],
    directionVector[2] * reference[0] -
      directionVector[0] * reference[2],
    directionVector[0] * reference[1] -
      directionVector[1] * reference[0],
  ]);

  const spacing = Math.max(inletWidth * 0.14, 0.035);
  const centeredIndex = index - (emitterCount - 1) / 2;

  return [
    perpendicular[0] * centeredIndex * spacing,
    perpendicular[1] * centeredIndex * spacing,
    perpendicular[2] * centeredIndex * spacing,
  ];
}

/**
 * Builds solver-backed flow segments.
 *
 * Duct:
 *   One independent segment per enabled fan with positive solver airflow.
 *
 * Outlet:
 *   One segment per outlet with positive solver airflow and available velocity.
 *
 * OFF fans generate no segment.
 */
export function buildFlowSegments(
  model: EngineeringSceneModel,
): FlowSegment[] {
  if (!model.hasSolverResult) {
    return [];
  }

  const inletEnd = solverToSceneVector(model.inlet.position);
  const inletDirection = normalizeVector(
    solverToSceneVector(model.inlet.direction),
  );

  const enabledFans = model.fanEmitters.filter(
    fan =>
      fan.enabled &&
      fan.current_airflow_cmh.value !== null &&
      (fan.current_airflow_cmh.value ?? 0) > 0,
  );

  const ductStartBase: [number, number, number] = [
    inletEnd[0] - inletDirection[0] * model.ductVisual.length,
    inletEnd[1] - inletDirection[1] * model.ductVisual.length,
    inletEnd[2] - inletDirection[2] * model.ductVisual.length,
  ];

  const ductSegments: FlowSegment[] = enabledFans.map((fan, index) => {
    const airflow = fan.current_airflow_cmh.value ?? 0;
    const ratedAirflow = fan.rated_airflow_cmh.value ?? 110000;

    const offset = buildEmitterOffset(
      inletDirection,
      index,
      enabledFans.length,
      model.inlet.width,
    );

    return {
      id: `duct-${fan.equipment_id}`,
      kind: "duct",
      sourceId: fan.equipment_id,

      start: [
        ductStartBase[0] + offset[0],
        ductStartBase[1] + offset[1],
        ductStartBase[2] + offset[2],
      ],

      direction: inletDirection,
      length: model.ductVisual.length,

      count: Math.max(
        1,
        Math.round((airflow / Math.max(ratedAirflow, 1)) * 10),
      ),

      engineeringSpeed: fan.inlet_velocity_mps.value ?? 0,
      engineeringAirflowCmh: airflow,
      color: index === 0 ? "#6dd9cf" : "#d8ff4f",
    };
  });

  const outletLength = Math.max(model.plenum.depth * 0.12, 0.12);

  const outletSegments: FlowSegment[] = model.outlets
    .filter(
      outlet =>
        outlet.airflowCmh !== null &&
        outlet.velocityMps !== null &&
        (outlet.airflowCmh ?? 0) > 0,
    )
    .map(outlet => ({
      id: `outlet-${outlet.id}`,
      kind: "outlet",
      sourceId: outlet.id,
      start: solverToSceneVector(outlet.position),
      direction: [0, -1, 0],
      length: outletLength,

      count: Math.max(
        1,
        Math.round(((outlet.airflowCmh ?? 0) / 220000) * 80),
      ),

      engineeringSpeed: outlet.velocityMps ?? 0,
      engineeringAirflowCmh: outlet.airflowCmh ?? 0,
      color: "#d8ff4f",
    }));

  return [...ductSegments, ...outletSegments];
}

/**
 * Backward-compatible alias.
 *
 * Existing callers can continue using buildParticleIndicators while the
 * visualization layer transitions to the FlowSegment terminology.
 */
export const buildParticleIndicators = buildFlowSegments;

export function buildEngineeringSceneModel(
  form: WorkspaceForm,
  result: SimulationResult | null,
  metric: HeatMetric,
): EngineeringSceneModel {
  const width = form.grille_width_mm / 1000;
  const height = form.grille_height_mm / 1000;
  const depth = form.plenum_depth_mm / 1000;
 const inletWidth = (form.inlet_width_mm ?? 1450) / 1000;
const inletHeight = (form.inlet_height_mm ?? 1450) / 1000;
  const outletWidth = form.outlet_width_mm / 1000;
  const outletHeight = form.outlet_height_mm / 1000;

  const resultByCell = new Map(
    result?.outlets.map(outlet => [
      `${outlet.row}:${outlet.column}`,
      outlet,
    ]) ?? [],
  );

  const available =
    result?.outlets
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

        position: [
          ((column + 0.5) / form.columns - 0.5) * width,
          (0.5 - (row + 0.5) / form.rows) * height,
          0,
        ],

        width: outletWidth,
        height: outletHeight,
        value,

        airflowPercentage:
          resultOutlet?.airflow_percentage.value ?? null,

        airflowCmh:
          resultOutlet?.airflow_cmh.value ?? null,

        velocityMps:
          resultOutlet?.outlet_velocity_mps.value ?? null,

        heat:
          numeric === null
            ? null
            : maximum === minimum
              ? 0.5
              : (numeric - minimum) / (maximum - minimum),
      });
    }
  }

  const directionMagnitude = Math.hypot(
    form.inlet.direction.x,
    form.inlet.direction.y,
    form.inlet.direction.z,
  );

  const direction: [number, number, number] =
    directionMagnitude === 0
      ? [0, 0, 0]
      : [
          form.inlet.direction.x / directionMagnitude,
          form.inlet.direction.y / directionMagnitude,
          form.inlet.direction.z / directionMagnitude,
        ];

  const inletPosition: [number, number, number] = [
    form.inlet.position.x,
    form.inlet.position.y,
    form.inlet.position.z,
  ];

  /*
   * Visualization-only estimate.
   *
   * This is intentionally not named ductLength or exposed as an engineering
   * result because the current input schema has no physical duct length.
   */
  const ductVisualLength = Math.max(depth * 0.75, 0.5);

  return {
    plenum: {
      width,
      height,
      depth,
    },

    inlet: {
      width: inletWidth,
      height: inletHeight,
      position: inletPosition,
      direction,
    },

    ductVisual: {
      width: inletWidth,
      height: inletHeight,
      length: ductVisualLength,
      endPosition: inletPosition,
      direction,
      estimatedLength: true,
    },

    outlets,
    deflectors: form.deflectors,
    fanEmitters: result?.fan_operating_results ?? [],
    hasSolverResult: result !== null,
  };
}
