export type Availability = "available" | "unavailable";

export interface Provenance {
  source_type: string;
  source_reference: string;
  solver_component: string | null;
  model_relationship: string | null;
}

export interface EngineeringValue {
  availability: Availability;
  value: number | null;
  unit: string | null;
  unavailable_reason: string | null;
  provenance: Provenance | null;
}

export interface DeflectorInput {
  identifier: string;
  position_m: { x: number; y: number; z: number };
  angle_deg_about_y: number;
  width_m: number;
  height_m: number;
}

export interface Vector3Input {
  x: number;
  y: number;
  z: number;
}

export interface InletBoundaryInput {
  position: Vector3Input;
  direction: Vector3Input;
}

export type FanEquipmentId = "SF-501" | "SF-502";

export interface FanOperatingInput {
  equipment_id: FanEquipmentId;
  enabled: boolean;
  frequency_hz: number;
}

export interface FanOperatingResult {
  equipment_id: FanEquipmentId;
  enabled: boolean;
  status: "OFF" | "STANDBY" | "RUNNING";
  frequency_hz: EngineeringValue;
  motor_power_hp: EngineeringValue;
  rated_airflow_cmh: EngineeringValue;
  rated_static_pressure_pa: EngineeringValue;
  maximum_frequency_hz: EngineeringValue;
  current_airflow_cmh: EngineeringValue;
  current_airflow_cfm: EngineeringValue;
  current_static_pressure_pa: EngineeringValue;
  inlet_velocity_mps: EngineeringValue;
  estimation_label: string;
}

/* ==========================================================
   Geometry V2
========================================================== */

export type InletShape = "rectangular" | "circular";

export interface SimulationRequest {
  // Outlet Grille
  grille_width_mm: number;
  grille_height_mm: number;

  // Plenum
  plenum_width_mm?: number;
  plenum_height_mm?: number;
  plenum_depth_mm: number;

  // Inlet Geometry
  inlet_shape?: InletShape;

  // Rectangular Inlet
  inlet_width_mm?: number;
  inlet_height_mm?: number;

  // Circular Inlet
  inlet_diameter_mm?: number;

  // Inlet Boundary
  inlet: InletBoundaryInput;

  // Fans
  fans: FanOperatingInput[];

  // Outlet Layout
  rows: number;
  columns: number;

  outlet_width_mm: number;
  outlet_height_mm: number;

  free_area_ratio: number | null;

  // Deflectors
  deflectors: DeflectorInput[];
}

export interface OutletResult {
  outlet_id: string;
  row: number;
  column: number;
  airflow_percentage: EngineeringValue;
  airflow_cfm: EngineeringValue;
  airflow_cmh: EngineeringValue;
  outlet_velocity_mps: EngineeringValue;
  geometric_area_m2: EngineeringValue;
  free_area_ratio: EngineeringValue;
  effective_area_m2: EngineeringValue;
  calculation_provenance: Record<string, EngineeringValue>;
}

export interface SimulationResult {
  status: "completed";
  solver: string;
  claim_label: string;
  experimental_notice: string;
  rows: number;
  columns: number;
  outlet_count: number;
  deflector_count: number;

  fan_operating_results: FanOperatingResult[];

  total_inlet_airflow_cfm: EngineeringValue;
  total_inlet_airflow_cmh: EngineeringValue;

  total_outlet_airflow_cfm: EngineeringValue;
  total_outlet_airflow_cmh: EngineeringValue;

  conservation_error_cfm: EngineeringValue;
  conserved: boolean;

  uniformity_index: EngineeringValue;

  outlets: OutletResult[];

  diagnostics: string[];
  assumptions: string[];
}
