import type { SimulationRequest } from "../../api/contracts";

export type InletDirectionPreset =
  | "downward"
  | "upward"
  | "leftToRight"
  | "rightToLeft"
  | "frontToBack"
  | "backToFront"
  | "custom";

export type FanFrequencyPreset =
  | "off"
  | "50"
  | "60"
  | "custom";

/**
 * Workspace 表單要求入口尺寸一定存在。
 *
 * SimulationRequest 為了相容 API，可能將入口尺寸定義為選填；
 * 但視覺化與操作介面必須始終有明確尺寸，因此在此重新定義為必填 number。
 */
export interface WorkspaceForm
  extends Omit<
    SimulationRequest,
    "free_area_ratio" | "inlet_width_mm" | "inlet_height_mm"
  > {
  inlet_width_mm: number;
  inlet_height_mm: number;

  free_area_percent: string;
  inlet_direction_preset: InletDirectionPreset;

  fan_frequency_presets: Record<
    "SF-501" | "SF-502",
    FanFrequencyPreset
  >;
}

/**
 * 下午會議討論版預設尺寸
 *
 * 格柵：1150 × 500 mm
 * 靜壓箱／格柵深度：150 mm
 * 圓形入口風管：Ø1450 mm
 * 格柵排列：2 列 × 4 欄
 */
export const INITIAL_FORM: WorkspaceForm = {
  grille_width_mm: 1150,
  grille_height_mm: 500,
  plenum_depth_mm: 150,

  inlet_width_mm: 1450,
  inlet_height_mm: 1450,

  inlet: {
    position: {
      x: 0,
      y: 0,
      z: 2,
    },
    direction: {
      x: 0,
      y: 0,
      z: -1,
    },
  },

  inlet_direction_preset: "downward",

  fans: [
    {
      equipment_id: "SF-501",
      enabled: true,
      frequency_hz: 50,
    },
    {
      equipment_id: "SF-502",
      enabled: false,
      frequency_hz: 0,
    },
  ],

  fan_frequency_presets: {
    "SF-501": "50",
    "SF-502": "off",
  },

  rows: 2,
  columns: 4,

  // 1150 ÷ 4 = 287.5 mm
  // 500 ÷ 2 = 250 mm
  outlet_width_mm: 287.5,
  outlet_height_mm: 250,

  free_area_percent: "70",

  deflectors: [
    {
      identifier: "D1",
      position_m: {
        x: 0,
        y: 0,
        z: 1,
      },
      angle_deg_about_y: 45,
      width_m: 0.2,
      height_m: 0.2,
    },
  ],
};

export function toSimulationRequest(
  form: WorkspaceForm,
): SimulationRequest {
  const {
    free_area_percent,
    inlet_direction_preset: _preset,
    fan_frequency_presets: _fanPresets,
    ...requestFields
  } = form;

  const entered = free_area_percent.trim();

  const { x, y, z } = form.inlet.direction;
  const magnitude = Math.hypot(x, y, z);

  if (!Number.isFinite(magnitude) || magnitude === 0) {
    throw new RangeError(
      "Inlet direction must be a finite non-zero vector",
    );
  }

  return {
    ...requestFields,

    inlet: {
      ...form.inlet,
      direction: {
        x: x / magnitude,
        y: y / magnitude,
        z: z / magnitude,
      },
    },

    free_area_ratio:
      entered === ""
        ? null
        : Number(entered) / 100,
  };
}
