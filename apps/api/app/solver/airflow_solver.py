"""Experimental replaceable airflow-distribution prototype V0.1.

The model is transparent and deterministic but not validated HVAC physics.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, pi, sin, sqrt
from typing import Protocol, Sequence

from .core import EngineeringValue, Provenance
from .geometry import Vector3
from .sequential_extraction import ExtractionInput, ExtractionPolicy, ExtractionProvenance, ExtractionSource, OutletExtractionInstruction, SequentialExtractionEvaluator


CFM_TO_CMH = 1.69901082


@dataclass(frozen=True, slots=True)
class AirflowPlenum:
    """Rectangular plenum domain in metres."""
    length_m: float
    width_m: float
    height_m: float


@dataclass(frozen=True, slots=True)
class AirflowInlet:
    """Explicit inlet geometry, unit direction, and supplied total airflow."""
    center_m: Vector3
    width_m: float
    height_m: float
    direction: Vector3
    total_airflow_cfm: float


@dataclass(frozen=True, slots=True)
class AirflowOutlet:
    """One outlet with allocation geometry and optional velocity geometry.

    ``width_m`` and ``height_m`` retain the V0.1 distribution contract.
    Millimetre dimensions and free-area ratio are separate, explicit inputs for
    velocity calculation; ``None`` means the corresponding input is unavailable.
    """
    outlet_id: str
    center_m: Vector3
    width_m: float
    height_m: float
    downstream_order: int
    width_mm: float | None = None
    height_mm: float | None = None
    free_area_ratio: float | None = None


@dataclass(frozen=True, slots=True)
class AirflowDeflector:
    """One rectangular plate rotated about global +Y."""
    deflector_id: str
    center_m: Vector3
    angle_deg_about_y: float
    width_m: float
    height_m: float


@dataclass(frozen=True, slots=True)
class ExperimentalAirflowInput:
    """Complete immutable prototype input."""
    plenum: AirflowPlenum
    inlet: AirflowInlet
    outlets: tuple[AirflowOutlet, ...]
    deflectors: tuple[AirflowDeflector, ...]


@dataclass(frozen=True, slots=True)
class ExperimentalAirflowPolicy:
    """Explicit numerical governance with no hidden defaults."""
    direction_tolerance: float
    conservation_tolerance_cfm: float
    tolerance_provenance: Provenance
    solver_version: str


@dataclass(frozen=True, slots=True)
class DeflectorAudit:
    """Experimental geometric influence audit for one plate."""
    deflector_id: str
    normal: Vector3
    projected_area_m2: float
    intercepted_fraction_proxy: float
    redirected_weights_usable: bool


@dataclass(frozen=True, slots=True)
class OutletAirflowEstimate:
    """Solver-owned outlet quantities; unavailable velocity is never guessed."""
    outlet_id: str
    downstream_order: int
    airflow_percentage: EngineeringValue[float]
    airflow_cfm: EngineeringValue[float]
    airflow_cmh: EngineeringValue[float]
    outlet_velocity_mps: EngineeringValue[float]
    calculation_provenance: OutletCalculationProvenance

    @property
    def estimated_airflow_cfm(self) -> EngineeringValue[float]:
        """Backward-compatible name for the unchanged V0.1 CFM result."""
        return self.airflow_cfm

    @property
    def percentage(self) -> EngineeringValue[float]:
        """Backward-compatible name for the unchanged V0.1 percentage result."""
        return self.airflow_percentage


@dataclass(frozen=True, slots=True)
class OutletCalculationProvenance:
    """Auditable inputs and intermediate quantities for outlet unit outputs."""
    total_inlet_airflow_cfm: EngineeringValue[float]
    cfm_to_cmh_conversion: EngineeringValue[float]
    geometric_outlet_area_m2: EngineeringValue[float]
    free_area_ratio: EngineeringValue[float]
    effective_outlet_area_m2: EngineeringValue[float]
    airflow_m3s: EngineeringValue[float]


@dataclass(frozen=True, slots=True)
class ExperimentalAirflowResult:
    """Completed prototype result with conservation and assumption labels."""
    completed: bool
    claim_label: str
    outlets: tuple[OutletAirflowEstimate, ...]
    supplied_total_cfm: EngineeringValue[float]
    estimated_total_cfm: EngineeringValue[float]
    terminal_remaining_cfm: EngineeringValue[float]
    conservation_residual_cfm: EngineeringValue[float]
    conserved: bool | None
    deflector_audit: tuple[DeflectorAudit, ...]
    assumptions: tuple[str, ...]
    diagnostics: tuple[str, ...]
    recommendation: None = None


class DistributionKernel(Protocol):
    """Replaceable geometric outlet-weight model."""
    def weights(self, origin: Vector3, direction: Vector3, outlets: Sequence[AirflowOutlet]) -> tuple[float, ...]:
        """Return non-negative unnormalized outlet weights."""
        ...


class DeflectorInfluenceModel(Protocol):
    """Replaceable experimental deflector influence model."""
    def apply(self, weights: tuple[float, ...], inlet: AirflowInlet, outlets: Sequence[AirflowOutlet], deflector: AirflowDeflector, kernel: DistributionKernel) -> tuple[tuple[float, ...], DeflectorAudit]:
        """Return influenced weights and a transparent audit."""
        ...


def _dot(a: Vector3, b: Vector3) -> float:
    return a.x*b.x+a.y*b.y+a.z*b.z


def _norm(a: Vector3) -> float:
    return sqrt(_dot(a,a))


def _sub(a: Vector3, b: Vector3) -> Vector3:
    return Vector3(a.x-b.x,a.y-b.y,a.z-b.z)


class DirectionalAreaDistanceKernel:
    """Experimental area/alignment/inverse-square distribution proxy."""
    def weights(self, origin: Vector3, direction: Vector3, outlets: Sequence[AirflowOutlet]) -> tuple[float, ...]:
        result=[]
        for outlet in outlets:
            delta=_sub(outlet.center_m,origin); distance=_norm(delta)
            if distance == 0: raise ValueError("outlet center cannot equal influence origin")
            unit=Vector3(delta.x/distance,delta.y/distance,delta.z/distance)
            alignment=max(0.0,_dot(direction,unit))
            result.append((outlet.width_m*outlet.height_m)*alignment/(distance*distance))
        return tuple(result)


class ProjectedAreaReflectionInfluence:
    """Experimental projected-area interception and geometric-reflection proxy."""
    def apply(self, weights, inlet, outlets, deflector, kernel):
        angle=deflector.angle_deg_about_y*pi/180.0
        normal=Vector3(sin(angle),0.0,cos(angle))
        projected=deflector.width_m*deflector.height_m*abs(_dot(inlet.direction,normal))
        inlet_area=inlet.width_m*inlet.height_m
        fraction=min(1.0,max(0.0,projected/inlet_area))
        reflected=Vector3(inlet.direction.x-2*_dot(inlet.direction,normal)*normal.x,inlet.direction.y-2*_dot(inlet.direction,normal)*normal.y,inlet.direction.z-2*_dot(inlet.direction,normal)*normal.z)
        redirected=kernel.weights(deflector.center_m,reflected,outlets)
        usable=sum(redirected)>0
        if fraction>0 and not usable: raise ValueError(f"deflector {deflector.deflector_id} redirected proxy has no usable outlet weights")
        if usable:
            redirected=_normalize(redirected)
            current=_normalize(weights)
            combined=tuple((1-fraction)*base+fraction*turn for base,turn in zip(current,redirected))
        else: combined=weights
        return combined,DeflectorAudit(deflector.deflector_id,normal,projected,fraction,usable)


def _normalize(weights: Sequence[float]) -> tuple[float, ...]:
    total=sum(weights)
    if not isfinite(total) or total<=0: raise ValueError("distribution weights have no usable positive total")
    return tuple(value/total for value in weights)


class ExperimentalAirflowSolver:
    """Orchestrate the replaceable prototype model and governed conservation."""
    ASSUMPTIONS=("directional_area_distance_proxy","projected_area_interception_proxy","geometric_reflection_redirection_proxy","ordered_deflector_mixing","shares_scaled_to_supplied_total_cfm")

    def __init__(self,kernel:DistributionKernel,influence:DeflectorInfluenceModel):
        self.kernel=kernel; self.influence=influence

    def solve(self,data:ExperimentalAirflowInput,policy:ExperimentalAirflowPolicy)->ExperimentalAirflowResult:
        """Validate, estimate, conserve, and package an experimental distribution."""
        try: self._validate(data,policy)
        except ValueError as exc: return self._failed(data,policy,str(exc))
        ordered=tuple(sorted(data.outlets,key=lambda item:item.downstream_order))
        try:
            weights=self.kernel.weights(data.inlet.center_m,data.inlet.direction,ordered); audits=[]
            weights=_normalize(weights)
            for deflector in data.deflectors:
                weights,audit=self.influence.apply(weights,data.inlet,ordered,deflector,self.kernel); weights=_normalize(weights); audits.append(audit)
            model_provenance=Provenance("experimental_solver",policy.solver_version,"experimental_airflow_solver","documented_v0.1_proxy")
            estimates_list=[]; remaining=data.inlet.total_airflow_cfm; cumulative_share=0.0
            for index,share in enumerate(weights):
                cumulative_share+=share
                target_remaining=0.0 if index==len(weights)-1 else data.inlet.total_airflow_cfm*(1.0-cumulative_share)
                extraction=remaining-target_remaining
                estimates_list.append(extraction)
                remaining=remaining-extraction
            estimates=tuple(estimates_list)
            instructions=tuple(OutletExtractionInstruction(outlet.outlet_id,EngineeringValue.available(value,"CFM",model_provenance),ExtractionProvenance(ExtractionSource.EXTERNALLY_EVALUATED,"experimental_airflow_solver_v0.1",policy.solver_version)) for outlet,value in zip(ordered,estimates))
            inlet_value=EngineeringValue.available(data.inlet.total_airflow_cfm,"CFM",Provenance("supplied_input","inlet.total_airflow_cfm"))
            conservation=SequentialExtractionEvaluator().evaluate(ExtractionInput(inlet_value,tuple(item.outlet_id for item in ordered),tuple(item.outlet_id for item in ordered),instructions),ExtractionPolicy("CFM",policy.conservation_tolerance_cfm,policy.tolerance_provenance,policy.solver_version))
            if not conservation.completed: return self._failed(data,policy,conservation.diagnostics[0].code)
            outlet_results=tuple(self._package_outlet(outlet,instruction.extracted,share,inlet_value,model_provenance) for outlet,instruction,share in zip(ordered,instructions,weights))
            return ExperimentalAirflowResult(True,"experimental_scaled_distribution",outlet_results,inlet_value,conservation.total_extracted,conservation.terminal_downstream,conservation.global_residual.residual,conservation.global_residual.conserved,tuple(audits),self.ASSUMPTIONS,())
        except ValueError as exc: return self._failed(data,policy,str(exc))

    def _package_outlet(self,outlet,airflow_cfm,share,inlet_value,model_provenance):
        """Add governed unit conversions without changing allocation values."""
        conversion=EngineeringValue.available(CFM_TO_CMH,"m^3/h per CFM",Provenance("defined_conversion","Behavior Fix 2","outlet_unit_conversion","airflow_cmh = airflow_cfm * 1.69901082"))
        airflow_cmh=EngineeringValue.available(airflow_cfm.value*CFM_TO_CMH,"m^3/h",Provenance("calculated",outlet.outlet_id,"outlet_unit_conversion","airflow_cmh = airflow_cfm * cfm_to_cmh_conversion"))
        airflow_m3s=EngineeringValue.available(airflow_cmh.value/3600.0,"m^3/s",Provenance("calculated",outlet.outlet_id,"outlet_unit_conversion","airflow_m3s = airflow_cmh / 3600"))
        area,ratio,effective,velocity=self._velocity_quantities(outlet,airflow_m3s)
        audit=OutletCalculationProvenance(inlet_value,conversion,area,ratio,effective,airflow_m3s)
        return OutletAirflowEstimate(outlet.outlet_id,outlet.downstream_order,EngineeringValue.available(share*100.0,"%",model_provenance),airflow_cfm,airflow_cmh,velocity,audit)

    def _velocity_quantities(self,outlet,airflow_m3s):
        """Return area-chain quantities or an unavailable velocity reason code."""
        area_unit="m^2"
        if outlet.width_mm is None:
            reason="OUTLET_VELOCITY_WIDTH_MM_UNAVAILABLE"
        elif not isfinite(outlet.width_mm) or outlet.width_mm<=0:
            reason="OUTLET_VELOCITY_WIDTH_MM_INVALID"
        elif outlet.height_mm is None:
            reason="OUTLET_VELOCITY_HEIGHT_MM_UNAVAILABLE"
        elif not isfinite(outlet.height_mm) or outlet.height_mm<=0:
            reason="OUTLET_VELOCITY_HEIGHT_MM_INVALID"
        elif outlet.free_area_ratio is None:
            reason="OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE"
        elif not isfinite(outlet.free_area_ratio) or not 0<outlet.free_area_ratio<=1:
            reason="OUTLET_VELOCITY_FREE_AREA_RATIO_INVALID"
        else:
            area_value=(outlet.width_mm/1000.0)*(outlet.height_mm/1000.0)
            area=EngineeringValue.available(area_value,area_unit,Provenance("calculated",outlet.outlet_id,"outlet_velocity","area_m2 = (width_mm / 1000) * (height_mm / 1000)"))
            ratio=EngineeringValue.available(outlet.free_area_ratio,"ratio",Provenance("supplied_input",f"outlets[{outlet.outlet_id}].free_area_ratio"))
            effective_value=area_value*outlet.free_area_ratio
            effective=EngineeringValue.available(effective_value,area_unit,Provenance("calculated",outlet.outlet_id,"outlet_velocity","effective_area_m2 = area_m2 * free_area_ratio"))
            velocity=EngineeringValue.available(airflow_m3s.value/effective_value,"m/s",Provenance("calculated",outlet.outlet_id,"outlet_velocity","outlet_velocity_mps = airflow_m3s / effective_area_m2"))
            return area,ratio,effective,velocity
        unavailable_area=EngineeringValue.unavailable(reason,area_unit)
        unavailable_ratio=EngineeringValue.unavailable(reason,"ratio")
        return unavailable_area,unavailable_ratio,unavailable_area,EngineeringValue.unavailable(reason,"m/s")

    def _validate(self,data,policy):
        numeric=(data.plenum.length_m,data.plenum.width_m,data.plenum.height_m,data.inlet.width_m,data.inlet.height_m,data.inlet.total_airflow_cfm,policy.direction_tolerance,policy.conservation_tolerance_cfm)
        if not all(isfinite(v) and v>0 for v in numeric): raise ValueError("positive finite dimensions, airflow, and tolerances are required")
        if not policy.solver_version: raise ValueError("solver version is required")
        if abs(_norm(data.inlet.direction)-1)>policy.direction_tolerance: raise ValueError("inlet direction must be an explicit unit vector")
        if len(data.outlets)!=8: raise ValueError("exactly eight outlets are required")
        ids=[item.outlet_id for item in data.outlets]; orders=[item.downstream_order for item in data.outlets]
        if len(set(ids))!=8 or sorted(orders)!=list(range(8)): raise ValueError("outlet IDs and downstream order must be unique and complete")
        if any(not item.outlet_id or item.width_m<=0 or item.height_m<=0 for item in data.outlets): raise ValueError("outlet geometry is invalid")
        deflector_ids=[item.deflector_id for item in data.deflectors]
        if len(deflector_ids)!=len(set(deflector_ids)) or any(not item.deflector_id or item.width_m<=0 or item.height_m<=0 or not isfinite(item.angle_deg_about_y) for item in data.deflectors): raise ValueError("deflector geometry is invalid")
        points=[data.inlet.center_m]+[item.center_m for item in data.outlets]+[item.center_m for item in data.deflectors]
        half_l=data.plenum.length_m/2; half_w=data.plenum.width_m/2
        if any(not all(isfinite(v) for v in (p.x,p.y,p.z)) or not(-half_l<=p.x<=half_l and -half_w<=p.y<=half_w and 0<=p.z<=data.plenum.height_m) for p in points): raise ValueError("component center lies outside plenum domain")

    def _failed(self,data,policy,message):
        unavailable=EngineeringValue.unavailable("experimental solver did not complete","CFM")
        supplied=EngineeringValue.available(data.inlet.total_airflow_cfm,"CFM",Provenance("supplied_input","inlet.total_airflow_cfm")) if isfinite(data.inlet.total_airflow_cfm) else unavailable
        return ExperimentalAirflowResult(False,"experimental_unavailable",(),supplied,unavailable,unavailable,unavailable,None,(),self.ASSUMPTIONS,(message,))
