import { describe, expect, it } from "vitest";
import type {
  FanOperatingResult,
  SimulationResult,
} from "../../api/contracts";
import { INITIAL_FORM } from "./initialState";
import {
  buildEngineeringSceneModel,
  buildFlowSegments,
  particleControlPoint,
  solverToSceneVector,
} from "./visualizationModel";

const engineeringValue = (
  value: number,
  unit: string,
) => ({
  availability: "available" as const,
  value,
  unit,
  unavailable_reason: null,
  provenance: null,
});

const result = {
  rows: 2,
  columns: 4,

  outlets: Array.from(
    { length: 8 },
    (_, index) => ({
      outlet_id: `R${Math.floor(index / 4)}C${index % 4}`,
      row: Math.floor(index / 4),
      column: index % 4,

      airflow_percentage: engineeringValue(
        8 + index,
        "%",
      ),

      airflow_cfm: engineeringValue(
        64 + index * 8,
        "CFM",
      ),

      airflow_cmh: engineeringValue(
        108 + index * 14,
        "m^3/h",
      ),

      outlet_velocity_mps: engineeringValue(
        1 + index / 10,
        "m/s",
      ),
    }),
  ),

  fan_operating_results: [],
} as unknown as SimulationResult;

const createFanResult = (
  equipmentId: "SF-501" | "SF-502",
  enabled: boolean,
  airflowCmh: number,
): FanOperatingResult => ({
  equipment_id: equipmentId,
  enabled,
  status: enabled ? "RUNNING" : "OFF",

  frequency_hz: engineeringValue(
    enabled ? 60 : 0,
    "Hz",
  ),

  motor_power_hp: engineeringValue(
    100,
    "HP",
  ),

  rated_airflow_cmh: engineeringValue(
    110000,
    "m^3/h",
  ),

  rated_static_pressure_pa: engineeringValue(
    1600,
    "Pa",
  ),

  maximum_frequency_hz: engineeringValue(
    60,
    "Hz",
  ),

  current_airflow_cmh: engineeringValue(
    airflowCmh,
    "m^3/h",
  ),

  current_airflow_cfm: engineeringValue(
    airflowCmh / 1.69901082,
    "CFM",
  ),

  current_static_pressure_pa: engineeringValue(
    enabled ? 1600 : 0,
    "Pa",
  ),

  inlet_velocity_mps: engineeringValue(
    enabled ? 190.97 : 0,
    "m/s",
  ),

  estimation_label:
    "Estimated using Fan Affinity Laws",
});

describe("engineering visualization projection", () => {
  it("maps geometry without requiring solver output", () => {
    const model = buildEngineeringSceneModel(
      INITIAL_FORM,
      null,
      "airflow_percentage",
    );

    expect(model.outlets).toHaveLength(8);
    expect(model.deflectors).toHaveLength(1);
    expect(model.hasSolverResult).toBe(false);

    expect(
      model.outlets.every(
        outlet =>
          outlet.value === null &&
          outlet.heat === null,
      ),
    ).toBe(true);
  });

  it("creates an explicitly estimated visual duct without presenting it as solver geometry", () => {
    const model = buildEngineeringSceneModel(
      INITIAL_FORM,
      null,
      "airflow_percentage",
    );

    expect(model.ductVisual.width).toBe(
      (INITIAL_FORM.inlet_width_mm ?? 1450) / 1000,
    );

    expect(model.ductVisual.height).toBe(
      (INITIAL_FORM.inlet_height_mm ?? 1450) / 1000,
    );

    expect(model.ductVisual.length).toBeGreaterThan(0);
    expect(model.ductVisual.estimatedLength).toBe(true);

    expect(model.ductVisual.endPosition).toEqual(
      model.inlet.position,
    );

    expect(model.ductVisual.direction).toEqual(
      model.inlet.direction,
    );
  });

  it("preserves solver values and only normalizes their visual heat", () => {
    const model = buildEngineeringSceneModel(
      INITIAL_FORM,
      result,
      "airflow_cfm",
    );

    expect(
      model.outlets.map(
        outlet => outlet.value?.value,
      ),
    ).toEqual(
      result.outlets.map(
        outlet => outlet.airflow_cfm.value,
      ),
    );

    expect(model.outlets[0].heat).toBe(0);
    expect(model.outlets[7].heat).toBe(1);
  });

  it("maps multiple deflectors directly from form geometry", () => {
    const second = {
      ...INITIAL_FORM.deflectors[0],
      identifier: "D2",

      position_m: {
        x: 0.4,
        y: 0.1,
        z: 0.6,
      },

      angle_deg_about_y: 30,
    };

    const form = {
      ...INITIAL_FORM,

      deflectors: [
        ...INITIAL_FORM.deflectors,
        second,
      ],
    };

    const model = buildEngineeringSceneModel(
      form,
      null,
      "airflow_percentage",
    );

    expect(model.deflectors).toEqual(
      form.deflectors,
    );
  });

  it("normalizes inlet direction and preserves its configured origin", () => {
    const form = {
      ...INITIAL_FORM,

      inlet: {
        position: {
          x: 0.2,
          y: -0.1,
          z: 1.7,
        },

        direction: {
          x: 1,
          y: 2,
          z: -2,
        },
      },
    };

    const model = buildEngineeringSceneModel(
      form,
      null,
      "airflow_percentage",
    );

    expect(model.inlet.position).toEqual([
      0.2,
      -0.1,
      1.7,
    ]);

    expect(model.inlet.direction).toEqual([
      1 / 3,
      2 / 3,
      -2 / 3,
    ]);
  });

  it("maps canonical solver directions to the same arrow and initial particle tangent", () => {
    const directions: [
      [number, number, number],
      string,
    ][] = [
      [[0, 0, -1], "down"],
      [[0, 0, 1], "up"],
      [[1, 0, 0], "left-to-right"],
      [[-1, 0, 0], "right-to-left"],
      [[0, 1, 0], "front-to-back"],
      [[0, -1, 0], "back-to-front"],
      [[1 / 3, 2 / 3, -2 / 3], "diagonal"],
    ];

    for (const [solverDirection] of directions) {
      const sceneDirection =
        solverToSceneVector(solverDirection);

      const start: [number, number, number] = [
        0,
        2,
        0,
      ];

      const control = particleControlPoint(
        start,
        sceneDirection,
        2,
      );

      const tangent = control.map(
        (value, index) =>
          (value - start[index]) / 0.6,
      );

      expect(tangent[0]).toBeCloseTo(
        sceneDirection[0],
      );

      expect(tangent[1]).toBeCloseTo(
        sceneDirection[1],
      );

      expect(tangent[2]).toBeCloseTo(
        sceneDirection[2],
      );
    }
  });

  it("creates no flow segments without solver output", () => {
    const model = buildEngineeringSceneModel(
      INITIAL_FORM,
      null,
      "airflow_percentage",
    );

    expect(buildFlowSegments(model)).toEqual([]);
  });

  it("creates outlet flow segments from solver outlet results", () => {
    const model = buildEngineeringSceneModel(
      INITIAL_FORM,
      result,
      "airflow_percentage",
    );

    const outletSegments =
      buildFlowSegments(model).filter(
        segment => segment.kind === "outlet",
      );

    expect(outletSegments).toHaveLength(8);

    expect(outletSegments[0].id).toBe(
      "outlet-R0C0",
    );

    expect(
      outletSegments[0].engineeringAirflowCmh,
    ).toBe(
      result.outlets[0].airflow_cmh.value,
    );

    expect(
      outletSegments[0].engineeringSpeed,
    ).toBe(
      result.outlets[0].outlet_velocity_mps.value,
    );
  });

  it("creates independent duct segments only for enabled solver-backed fans", () => {
    const oneFanResult = {
      ...result,

      fan_operating_results: [
        createFanResult(
          "SF-501",
          true,
          110000,
        ),

        createFanResult(
          "SF-502",
          false,
          0,
        ),
      ],
    } as SimulationResult;

    const oneFanSegments = buildFlowSegments(
      buildEngineeringSceneModel(
        INITIAL_FORM,
        oneFanResult,
        "airflow_percentage",
      ),
    ).filter(
      segment => segment.kind === "duct",
    );

    expect(
      oneFanSegments.map(
        segment => segment.id,
      ),
    ).toEqual([
      "duct-SF-501",
    ]);

    expect(oneFanSegments[0].sourceId).toBe(
      "SF-501",
    );

    expect(oneFanSegments[0].count).toBe(10);

    expect(
      oneFanSegments[0].engineeringAirflowCmh,
    ).toBe(110000);

    const twoFanResult = {
      ...result,

      fan_operating_results: [
        createFanResult(
          "SF-501",
          true,
          110000,
        ),

        createFanResult(
          "SF-502",
          true,
          55000,
        ),
      ],
    } as SimulationResult;

    const twoFanSegments = buildFlowSegments(
      buildEngineeringSceneModel(
        INITIAL_FORM,
        twoFanResult,
        "airflow_percentage",
      ),
    ).filter(
      segment => segment.kind === "duct",
    );

    expect(
      twoFanSegments.map(
        segment => segment.id,
      ),
    ).toEqual([
      "duct-SF-501",
      "duct-SF-502",
    ]);

    expect(twoFanSegments[0].count).toBe(10);
    expect(twoFanSegments[1].count).toBe(5);

    expect(
      twoFanSegments[0].direction,
    ).toEqual(
      twoFanSegments[1].direction,
    );

    expect(
      twoFanSegments[0].start,
    ).not.toEqual(
      twoFanSegments[1].start,
    );
  });

  it("does not create a duct segment for an OFF fan even if malformed airflow is present", () => {
    const malformedResult = {
      ...result,

      fan_operating_results: [
        createFanResult(
          "SF-501",
          false,
          110000,
        ),
      ],
    } as SimulationResult;

    const ductSegments = buildFlowSegments(
      buildEngineeringSceneModel(
        INITIAL_FORM,
        malformedResult,
        "airflow_percentage",
      ),
    ).filter(
      segment => segment.kind === "duct",
    );

    expect(ductSegments).toEqual([]);
  });
});
