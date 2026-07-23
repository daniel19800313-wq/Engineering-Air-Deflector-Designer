import type {
  InletShape,
  SimulationRequest,
} from "../../api/contracts";

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
 * SimulationRequest 為了相容 API，可能將入口尺寸定義為選填，
 * 尤其是圓形入口時；但 Workspace 始終維持數值存在，
 * 讓使用者可以安全地在圓形與矩形入口之間切換，
 * 因此在此重新定義為必填 number。
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

const DEFAULT_INLET_SHAPE: InletShape = "circular";

/**
 * 現場設備預設尺寸
 *
 * 圓形入口風管：Ø1450 mm
 * 格柵：1150 × 500 × 150 mm
 * 格柵排列：2 列 × 4 欄
 *
 * 現場結構為圓風管直接連接格柵，沒有獨立靜壓箱。
 * 現階段 plenum_depth_mm 暫時代表格柵／出風段深度。
 */
export const INITIAL_FORM: WorkspaceForm = {
  plenum_width_mm: 1450,
  plenum_height_mm: 1450,
  plenum_depth_mm: 150,

  grille_width_mm: 1150,
  grille_height_mm: 500,

  inlet_shape: DEFAULT_INLET_SHAPE,
  inlet_diameter_mm: 1450,

  /**
   * 保留作為矩形入口的預設尺寸。
   * 當 inlet_shape 從 circular 切換為 rectangular 時使用。
   */
  inlet_width_mm: 1450,
  inlet_height_mm: 1450,

  inlet: {
    position: {
      x: 0,
      y: 0,
      z: 0.15,
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
        z: 0.075,
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
    inlet_direction_preset: _inletDirectionPreset,
    fan_frequency_presets: _fanFrequencyPresets,
    ...requestFields
  } = form;

  const enteredFreeAreaPercent = free_area_percent.trim();

  const { x, y, z } = form.inlet.direction;
  const magnitude = Math.hypot(x, y, z);

  if (!Number.isFinite(magnitude) || magnitude === 0) {
    throw new RangeError(
      "Inlet direction must be a finite non-zero vector",
    );
  }

  const normalizedDirection = {
    x: x / magnitude,
    y: y / magnitude,
    z: z / magnitude,
  };

  const parsedFreeAreaRatio =
    enteredFreeAreaPercent === ""
      ? null
      : Number(enteredFreeAreaPercent) / 100;

  if (
    parsedFreeAreaRatio !== null &&
    (
      !Number.isFinite(parsedFreeAreaRatio) ||
      parsedFreeAreaRatio <= 0 ||
      parsedFreeAreaRatio > 1
    )
  ) {
    throw new RangeError(
      "Free area percentage must be greater than 0 and no more than 100",
    );
  }

  const inletShape =
    requestFields.inlet_shape ?? "rectangular";

  if (
    inletShape === "circular" &&
    (
      requestFields.inlet_diameter_mm === undefined ||
      !Number.isFinite(requestFields.inlet_diameter_mm) ||
      requestFields.inlet_diameter_mm <= 0
    )
  ) {
    throw new RangeError(
      "Circular inlet diameter must be greater than zero",
    );
  }

  if (
    inletShape === "rectangular" &&
    (
      requestFields.inlet_width_mm === undefined ||
      requestFields.inlet_height_mm === undefined ||
      !Number.isFinite(requestFields.inlet_width_mm) ||
      !Number.isFinite(requestFields.inlet_height_mm) ||
      requestFields.inlet_width_mm <= 0 ||
      requestFields.inlet_height_mm <= 0
    )
  ) {
    throw new RangeError(
      "Rectangular inlet width and height must be greater than zero",
    );
  }

  return {
    ...requestFields,

    inlet: {
      ...form.inlet,
      direction: normalizedDirection,
    },

    free_area_ratio: parsedFreeAreaRatio,
  };
}