"""FastAPI contract for the Experimental Airflow Solver V0.1 workspace."""
from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.solver.airflow_solver import (
    AirflowDeflector,
    AirflowInlet,
    AirflowOutlet,
    AirflowPlenum,
    CFM_TO_CMH,
    DirectionalAreaDistanceKernel,
    ExperimentalAirflowInput,
    ExperimentalAirflowPolicy,
    ExperimentalAirflowSolver,
    ProjectedAreaReflectionInfluence,
)
from app.solver.core import EngineeringValue, Provenance
from app.solver.geometry import Vector3


router = APIRouter(prefix="/simulations", tags=["simulations"])
POLICY = ExperimentalAirflowPolicy(
    0.000001,
    0.000001,
    Provenance("api_policy", "simulation-workspace-v0.1"),
    "experimental-airflow-v0.1",
)


class StrictModel(BaseModel):
    """Forbid undeclared request fields at the HTTP boundary."""

    model_config = ConfigDict(extra="forbid")


class PointInput(StrictModel):
    """Point in the solver's metre coordinate system."""

    x: float
    y: float
    z: float


class DeflectorInput(StrictModel):
    """Deflector fields already supported by the V0.1 solver."""

    identifier: str = Field(min_length=1)
    position_m: PointInput
    angle_deg_about_y: float
    width_m: float = Field(gt=0)
    height_m: float = Field(gt=0)


class InletBoundaryInput(StrictModel):
    """Explicit inlet center and direction in canonical solver coordinates."""

    position: PointInput
    direction: PointInput


class FanOperatingInput(StrictModel):
    """User-selected operating state for a verified site fan profile."""

    equipment_id: Literal["SF-501", "SF-502"]
    enabled: bool
    frequency_hz: float = Field(ge=0, le=60)


class WorkspaceSimulationRequest(StrictModel):
    """Editable workspace inputs with explicit units and no guessed free area."""

    grille_width_mm: float = Field(gt=0)
    grille_height_mm: float = Field(gt=0)
    plenum_width_mm: float | None = Field(default=None, gt=0)
    plenum_height_mm: float | None = Field(default=None, gt=0)
    plenum_depth_mm: float = Field(gt=0)

    inlet_shape: Literal["rectangular", "circular"] = "rectangular"
    inlet_width_mm: float | None = Field(default=None, gt=0)
    inlet_height_mm: float | None = Field(default=None, gt=0)
    inlet_diameter_mm: float | None = Field(default=None, gt=0)
    inlet: InletBoundaryInput
    fans: tuple[FanOperatingInput, ...]
    rows: int = Field(gt=0)
    columns: int = Field(gt=0)
    outlet_width_mm: float = Field(gt=0)
    outlet_height_mm: float = Field(gt=0)
    free_area_ratio: float | None = Field(default=None, gt=0, le=1)
    deflectors: tuple[DeflectorInput, ...]


def _value(value: EngineeringValue[float]) -> dict[str, Any]:
    """Serialize availability, unit, provenance, and reason without defaults."""

    provenance = value.provenance
    return {
        "availability": value.availability.value,
        "value": value.value,
        "unit": value.unit,
        "unavailable_reason": value.unavailable_reason,
        "provenance": None if provenance is None else {
            "source_type": provenance.source_type,
            "source_reference": provenance.source_reference,
            "solver_component": provenance.solver_component,
            "model_relationship": provenance.model_relationship,
        },
    }


FAN_PROFILES = {
    "SF-501": {"motor_power_hp": 100.0, "rated_airflow_cmh": 110000.0, "rated_static_pressure_pa": 1600.0, "maximum_frequency_hz": 60.0},
    "SF-502": {"motor_power_hp": 100.0, "rated_airflow_cmh": 110000.0, "rated_static_pressure_pa": 1600.0, "maximum_frequency_hz": 60.0},
}


def _fan_operating_results(request: WorkspaceSimulationRequest) -> tuple[tuple[dict[str, Any], ...], float]:
    """Apply the approved fan affinity relationships; no fan curve is inferred."""

    identifiers = [fan.equipment_id for fan in request.fans]
    if sorted(identifiers) != sorted(FAN_PROFILES):
        raise HTTPException(422, detail="Exactly one SF-501 and one SF-502 operating input are required")
    results = []
    total_cfm = 0.0
    for fan in request.fans:
        profile = FAN_PROFILES[fan.equipment_id]
        effective_hz = fan.frequency_hz if fan.enabled else 0.0
        ratio = effective_hz / profile["maximum_frequency_hz"]
        airflow_cmh = profile["rated_airflow_cmh"] * ratio
        airflow_cfm = airflow_cmh / CFM_TO_CMH
        pressure_pa = profile["rated_static_pressure_pa"] * ratio * ratio
        inlet_area_m2 = (request.inlet_width_mm / 1000.0) * (request.inlet_height_mm / 1000.0)
        inlet_velocity_mps = (airflow_cmh / 3600.0) / inlet_area_m2
        total_cfm += airflow_cfm
        provenance = Provenance("calculated", f"{fan.equipment_id} verified nameplate", "fan_affinity_model", "estimated using Fan Affinity Laws")
        results.append({
            "equipment_id": fan.equipment_id,
            "enabled": fan.enabled,
            "status": "OFF" if not fan.enabled else ("STANDBY" if effective_hz == 0 else "RUNNING"),
            "frequency_hz": _value(EngineeringValue.available(effective_hz, "Hz", Provenance("supplied_input", f"fans[{fan.equipment_id}].frequency_hz"))),
            "motor_power_hp": _value(EngineeringValue.available(profile["motor_power_hp"], "HP", Provenance("verified_nameplate", fan.equipment_id))),
            "rated_airflow_cmh": _value(EngineeringValue.available(profile["rated_airflow_cmh"], "m^3/h", Provenance("verified_nameplate", fan.equipment_id))),
            "rated_static_pressure_pa": _value(EngineeringValue.available(profile["rated_static_pressure_pa"], "Pa", Provenance("verified_nameplate", fan.equipment_id))),
            "maximum_frequency_hz": _value(EngineeringValue.available(profile["maximum_frequency_hz"], "Hz", Provenance("verified_nameplate", fan.equipment_id))),
            "current_airflow_cmh": _value(EngineeringValue.available(airflow_cmh, "m^3/h", provenance)),
            "current_airflow_cfm": _value(EngineeringValue.available(airflow_cfm, "CFM", provenance)),
            "current_static_pressure_pa": _value(EngineeringValue.available(pressure_pa, "Pa", provenance)),
            "inlet_velocity_mps": _value(EngineeringValue.available(inlet_velocity_mps, "m/s", Provenance("calculated", f"{fan.equipment_id} affinity-law airflow and shared inlet area", "fan_inlet_velocity", "airflow_m3s / inlet_area_m2"))),
            "estimation_label": "Estimated using Fan Affinity Laws",
        })
    if total_cfm <= 0:
        raise HTTPException(422, detail="At least one enabled fan must operate above 0 Hz")
    return tuple(results), total_cfm


def _solver_input(request: WorkspaceSimulationRequest, total_airflow_cfm: float | None = None) -> ExperimentalAirflowInput:
    """Build explicit V0.1 geometry; the adapter does not calculate airflow."""

    if request.rows * request.columns != 8:
        raise HTTPException(422, detail="Experimental Airflow Solver V0.1 requires exactly eight outlets")
    grille_width_m = request.grille_width_mm / 1000.0
    grille_height_m = request.grille_height_mm / 1000.0
    plenum_width_m = (request.plenum_width_mm if request.plenum_width_mm is not None else request.grille_width_mm) / 1000.0
    plenum_height_m = (request.plenum_height_mm if request.plenum_height_mm is not None else request.grille_height_mm) / 1000.0
    depth_m = request.plenum_depth_mm / 1000.0

    if grille_width_m > plenum_width_m or grille_height_m > plenum_height_m:
        raise HTTPException(422, detail="Grille cannot be larger than plenum")

    if request.inlet_shape == "rectangular":
        inlet_width_m = (request.inlet_width_mm or 0) / 1000.0
        inlet_height_m = (request.inlet_height_mm or 0) / 1000.0
    else:
        import math
        if request.inlet_diameter_mm is None:
            raise HTTPException(422, detail="Circular inlet requires inlet_diameter_mm")
        diameter_m = request.inlet_diameter_mm / 1000.0
        side = math.sqrt(math.pi * (diameter_m / 2.0) ** 2)
        inlet_width_m = side
        inlet_height_m = side
    direction = request.inlet.direction
    direction_magnitude = (direction.x ** 2 + direction.y ** 2 + direction.z ** 2) ** 0.5
    if direction_magnitude == 0.0:
        raise HTTPException(422, detail="Inlet direction vector must not be zero length")
    normalized_direction = Vector3(
        direction.x / direction_magnitude,
        direction.y / direction_magnitude,
        direction.z / direction_magnitude,
    )
    cell_pitch_x = grille_width_m / request.columns
    cell_pitch_y = grille_height_m / request.rows
    outlets = tuple(
        AirflowOutlet(
            outlet_id=f"R{row}C{column}",
            center_m=Vector3(
                -grille_width_m / 2 + cell_pitch_x * (column + 0.5),
                -grille_height_m / 2 + cell_pitch_y * (row + 0.5),
                0.0,
            ),
            width_m=request.outlet_width_mm / 1000.0,
            height_m=request.outlet_height_mm / 1000.0,
            downstream_order=row * request.columns + column,
            width_mm=request.outlet_width_mm,
            height_mm=request.outlet_height_mm,
            free_area_ratio=request.free_area_ratio,
        )
        for row in range(request.rows)
        for column in range(request.columns)
    )
    deflectors = tuple(
        AirflowDeflector(
            item.identifier,
            Vector3(item.position_m.x, item.position_m.y, item.position_m.z),
            item.angle_deg_about_y,
            item.width_m,
            item.height_m,
        )
        for item in request.deflectors
    )
    if total_airflow_cfm is None:
        _, total_airflow_cfm = _fan_operating_results(request)
    return ExperimentalAirflowInput(
        AirflowPlenum(plenum_width_m, plenum_height_m, depth_m),
        AirflowInlet(
            Vector3(request.inlet.position.x, request.inlet.position.y, request.inlet.position.z),
            inlet_width_m,
            inlet_height_m,
            normalized_direction,
            total_airflow_cfm,
        ),
        outlets,
        deflectors,
    )


@router.post("/airflow")
def run_airflow_simulation(request: WorkspaceSimulationRequest) -> dict[str, Any]:
    """Run the existing solver and return only solver-owned engineering values."""

    fan_results, total_airflow_cfm = _fan_operating_results(request)
    result = ExperimentalAirflowSolver(
        DirectionalAreaDistanceKernel(), ProjectedAreaReflectionInfluence()
    ).solve(_solver_input(request, total_airflow_cfm), POLICY)
    if not result.completed:
        raise HTTPException(422, detail={"message": "Solver did not complete", "diagnostics": result.diagnostics})
    outlets = []
    for item in result.outlets:
        audit = item.calculation_provenance
        outlets.append({
            "outlet_id": item.outlet_id,
            "row": item.downstream_order // request.columns,
            "column": item.downstream_order % request.columns,
            "airflow_percentage": _value(item.airflow_percentage),
            "airflow_cfm": _value(item.airflow_cfm),
            "airflow_cmh": _value(item.airflow_cmh),
            "outlet_velocity_mps": _value(item.outlet_velocity_mps),
            "geometric_area_m2": _value(audit.geometric_outlet_area_m2),
            "free_area_ratio": _value(audit.free_area_ratio),
            "effective_area_m2": _value(audit.effective_outlet_area_m2),
            "calculation_provenance": {
                "total_inlet_airflow_cfm": _value(audit.total_inlet_airflow_cfm),
                "cfm_to_cmh_conversion": _value(audit.cfm_to_cmh_conversion),
                "airflow_m3s": _value(audit.airflow_m3s),
                "final_velocity": _value(item.outlet_velocity_mps),
            },
        })
    percentages = [item.airflow_percentage.value for item in result.outlets]
    uniformity = min(percentages) / max(percentages)
    total_cmh = sum(item.airflow_cmh.value for item in result.outlets)
    return {
        "status": "completed",
        "solver": "Experimental Airflow Solver V0.1",
        "claim_label": result.claim_label,
        "experimental_notice": "This is an experimental distribution model, not CFD. It does not model pressure, turbulence, resistance, or full fluid dynamics.",
        "rows": request.rows,
        "columns": request.columns,
        "outlet_count": len(outlets),
        "deflector_count": len(request.deflectors),
        "fan_operating_results": list(fan_results),
        "total_inlet_airflow_cfm": _value(result.supplied_total_cfm),
        "total_inlet_airflow_cmh": _value(EngineeringValue.available(total_airflow_cfm * CFM_TO_CMH, "m^3/h", Provenance("calculated", "sum of SF-501 and SF-502 affinity-law airflow", "fan_affinity_model", "SF-501 airflow + SF-502 airflow"))),
        "total_outlet_airflow_cfm": _value(result.estimated_total_cfm),
        "total_outlet_airflow_cmh": _value(EngineeringValue.available(total_cmh, "m^3/h", Provenance("calculated", "sum of solver outlet airflow_cmh", "simulation_api", "sum(outlet.airflow_cmh)"))),
        "conservation_error_cfm": _value(result.conservation_residual_cfm),
        "conserved": result.conserved,
        "uniformity_index": _value(EngineeringValue.available(uniformity, "ratio", Provenance("calculated", "solver outlet results", "simulation_api", "minimum airflow percentage / maximum airflow percentage"))),
        "outlets": outlets,
        "diagnostics": list(result.diagnostics),
        "assumptions": list(result.assumptions),
    }
