import type { Dispatch, SetStateAction } from "react";
import { useI18n } from "../../i18n/i18n";
import type { SimulationResult } from "../../api/contracts";
import { formatValue } from "./format";
import type { FanFrequencyPreset,InletDirectionPreset,WorkspaceForm } from "./initialState";

export interface WorkspaceError { message:string; technical?:string }
type Props = {form:WorkspaceForm;result:SimulationResult|null;setForm:Dispatch<SetStateAction<WorkspaceForm>>;running:boolean;errors:WorkspaceError[];onRun:()=>void;onReset:()=>void};
const number=(value:string)=>value===""?0:Number(value);
const PRESET_DIRECTIONS:Record<Exclude<InletDirectionPreset,"custom">,{x:number;y:number;z:number}>={downward:{x:0,y:0,z:-1},upward:{x:0,y:0,z:1},leftToRight:{x:1,y:0,z:0},rightToLeft:{x:-1,y:0,z:0},frontToBack:{x:0,y:1,z:0},backToFront:{x:0,y:-1,z:0}};

export function InputPanel({form,result,setForm,running,errors,onRun,onReset}:Props){
  const {t}=useI18n();
  const inletForPreset=(current:WorkspaceForm,preset:Exclude<InletDirectionPreset,"custom">)=>{
    const halfX=Number(current.grille_width_mm)/2000;
    const halfY=Number(current.grille_height_mm)/2000;
    const topZ=Number(current.plenum_depth_mm)/1000;
    const centerZ=topZ/2;

    switch(preset){
      case "leftToRight":
        return {position:{x:-halfX,y:0,z:centerZ},direction:PRESET_DIRECTIONS[preset]};
      case "rightToLeft":
        return {position:{x:halfX,y:0,z:centerZ},direction:PRESET_DIRECTIONS[preset]};
      case "frontToBack":
        return {position:{x:0,y:-halfY,z:centerZ},direction:PRESET_DIRECTIONS[preset]};
      case "backToFront":
        return {position:{x:0,y:halfY,z:centerZ},direction:PRESET_DIRECTIONS[preset]};
      case "downward":
        return {position:{x:0,y:0,z:topZ},direction:PRESET_DIRECTIONS[preset]};
      case "upward":
        return {position:{x:0,y:0,z:0},direction:PRESET_DIRECTIONS[preset]};
    }
  };

  const update=(key:keyof WorkspaceForm,value:number|string)=>setForm(current=>{
    const next={...current,[key]:value};
    if(
      current.inlet_direction_preset!=="custom"&&
      (key==="grille_width_mm"||key==="grille_height_mm"||key==="plenum_depth_mm")
    ){
      return {...next,inlet:inletForPreset(next,current.inlet_direction_preset)};
    }
    return next;
  });
  const updateDeflector=(index:number,patch:Record<string,unknown>)=>setForm(current=>({...current,deflectors:current.deflectors.map((item,i)=>i===index?{...item,...patch}:item)}));
  const updatePosition=(index:number,axis:"x"|"y"|"z",value:number)=>setForm(current=>({...current,deflectors:current.deflectors.map((item,i)=>i===index?{...item,position_m:{...item.position_m,[axis]:value}}:item)}));
  const updateInlet=(part:"position"|"direction",axis:"x"|"y"|"z",value:number)=>setForm(current=>({
    ...current,
    inlet:{
      ...current.inlet,
      [part]:{
        ...current.inlet[part],
        [axis]:value,
      },
    },
    inlet_direction_preset:"custom",
  }));
  const selectPreset=(preset:InletDirectionPreset)=>setForm(current=>({
    ...current,
    inlet_direction_preset:preset,
    inlet:preset==="custom"?current.inlet:inletForPreset(current,preset),
  }));
  const updateFan=(equipmentId:"SF-501"|"SF-502",patch:{enabled?:boolean;frequency_hz?:number},preset?:FanFrequencyPreset)=>setForm(current=>({...current,fans:current.fans.map(fan=>fan.equipment_id===equipmentId?{...fan,...patch}:fan),fan_frequency_presets:{...current.fan_frequency_presets,[equipmentId]:preset??"custom"}}));
  const selectFanPreset=(equipmentId:"SF-501"|"SF-502",preset:FanFrequencyPreset)=>{if(preset==="off")updateFan(equipmentId,{enabled:false,frequency_hz:0},preset);else if(preset==="50"||preset==="60")updateFan(equipmentId,{enabled:true,frequency_hz:Number(preset)},preset);else updateFan(equipmentId,{enabled:true},preset)};
  return <aside className="panel input-panel" aria-labelledby="inputs-title">
    <div className="section-heading"><span className="eyebrow">{t("simulationInput")}</span><h2 id="inputs-title">{t("designParameters")}</h2></div>
    <fieldset><legend>{t("inletSection")}</legend><div className="field-grid">
      <label>{t("inletWidth")} <span>mm</span><input aria-label={`${t("inletWidth")} mm`} type="number" min="0" value={form.inlet_width_mm} onChange={e=>update("inlet_width_mm",number(e.target.value))}/></label>
      <label>{t("inletHeight")} <span>mm</span><input aria-label={`${t("inletHeight")} mm`} type="number" min="0" value={form.inlet_height_mm} onChange={e=>update("inlet_height_mm",number(e.target.value))}/></label>
    </div><div className="inlet-boundary">
      <h3>{t("inletBoundary")}</h3><label className="preset-field">{t("directionPreset")}<select aria-label={t("directionPreset")} value={form.inlet_direction_preset} onChange={event=>selectPreset(event.target.value as InletDirectionPreset)}><option value="downward">{t("presetDownward")}</option><option value="upward">{t("presetUpward")}</option><option value="leftToRight">{t("presetLeftToRight")}</option><option value="rightToLeft">{t("presetRightToLeft")}</option><option value="frontToBack">{t("presetFrontToBack")}</option><option value="backToFront">{t("presetBackToFront")}</option><option value="custom">{t("presetCustom")}</option></select></label>
      <div className="vector-group">
        <span>{t("inletPosition")} <small>m</small></span>
        <div className="vector-fields">
          {(["x","y","z"] as const).map(axis=><label key={axis}>{axis.toUpperCase()}<input aria-label={`${t("inletPosition")} ${axis.toUpperCase()}`} type="number" step="0.01" value={form.inlet.position[axis]} onChange={event=>updateInlet("position",axis,number(event.target.value))}/></label>)}
        </div>
      </div>
      <div className="vector-group">
        <span>{t("inletDirection")} <small>{t("normalizedOnRun")}</small></span>
        <div className="vector-fields">
          {(["x","y","z"] as const).map(axis=><label key={axis}>{axis.toUpperCase()}<input aria-label={`${t("inletDirection")} ${axis.toUpperCase()}`} type="number" step="0.1" value={form.inlet.direction[axis]} onChange={event=>updateInlet("direction",axis,number(event.target.value))}/></label>)}
        </div>
      </div>
      <p className="field-note coordinate-note">選擇方向預設時會自動帶入座標；手動修改任何座標後會切換為自訂模式。</p>
    </div></fieldset>
    <fieldset><legend>{t("fanSection")}</legend><div className="fan-list">{form.fans.map(fan=>{const operating=result?.fan_operating_results?.find(item=>item.equipment_id===fan.equipment_id);return <section className="fan-card" key={fan.equipment_id} aria-label={fan.equipment_id}>
      <div className="fan-head"><strong>{fan.equipment_id}</strong><label><input aria-label={`${fan.equipment_id} ${t("enabled")}`} type="checkbox" checked={fan.enabled} onChange={event=>updateFan(fan.equipment_id,{enabled:event.target.checked},event.target.checked?"custom":"off")}/>{fan.enabled?t("enabled"):t("disabled")}</label></div>
      <div className="fan-nameplate"><span>100 HP</span><span>110000 m³/h</span><span>1600 Pa</span><span>60 Hz max</span></div>
      <div className="field-grid compact"><label>{t("fanPreset")}<select aria-label={`${fan.equipment_id} ${t("fanPreset")}`} value={form.fan_frequency_presets[fan.equipment_id]} onChange={event=>selectFanPreset(fan.equipment_id,event.target.value as FanFrequencyPreset)}><option value="off">OFF</option><option value="50">50 Hz</option><option value="60">60 Hz</option><option value="custom">{t("fanCustom")}</option></select></label><label>{t("frequency")} <span>Hz</span><input aria-label={`${fan.equipment_id} ${t("frequency")} Hz`} type="number" min="0" max="60" value={fan.frequency_hz} disabled={form.fan_frequency_presets[fan.equipment_id]!=="custom"} onChange={event=>updateFan(fan.equipment_id,{frequency_hz:number(event.target.value)},"custom")}/></label></div>
      <dl className="fan-readout"><div><dt>{t("currentStatus")}</dt><dd>{operating?t(`fanStatus${operating.status}` as "fanStatusOFF"|"fanStatusSTANDBY"|"fanStatusRUNNING"):t("awaitingSolver")}</dd></div><div><dt>{t("currentAirflow")}</dt><dd>{operating?formatValue(operating.current_airflow_cmh):t("unavailable")}</dd></div><div><dt>{t("currentPressure")}</dt><dd>{operating?formatValue(operating.current_static_pressure_pa):t("unavailable")}</dd></div></dl>
      <p className="fan-estimate">{operating?t("affinityEstimate"):t("runForFanEstimate")}</p>
    </section>})}</div></fieldset>
    <fieldset><legend>{t("grilleSection")}</legend><div className="field-grid">
      <label>{t("grilleWidth")} <span>mm</span><input aria-label={`${t("grilleWidth")} mm`} type="number" min="0" value={form.grille_width_mm} onChange={e=>update("grille_width_mm",number(e.target.value))}/></label>
      <label>{t("grilleHeight")} <span>mm</span><input aria-label={`${t("grilleHeight")} mm`} type="number" min="0" value={form.grille_height_mm} onChange={e=>update("grille_height_mm",number(e.target.value))}/></label>
      <label>{t("plenumDepth")} <span>mm</span><input aria-label={`${t("plenumDepth")} mm`} type="number" min="0" value={form.plenum_depth_mm} onChange={e=>update("plenum_depth_mm",number(e.target.value))}/></label>
    </div></fieldset>
    <fieldset><legend>{t("outletSection")}</legend><div className="field-grid">
      <label>{t("rows")} <span>{t("count")}</span><input aria-label={t("rows")} type="number" min="1" step="1" value={form.rows} onChange={e=>update("rows",number(e.target.value))}/></label>
      <label>{t("columns")} <span>{t("count")}</span><input aria-label={t("columns")} type="number" min="1" step="1" value={form.columns} onChange={e=>update("columns",number(e.target.value))}/></label>
      <label>{t("outletWidth")} <span>mm</span><input aria-label={`${t("outletWidth")} mm`} type="number" min="0" value={form.outlet_width_mm} onChange={e=>update("outlet_width_mm",number(e.target.value))}/></label>
      <label>{t("outletHeight")} <span>mm</span><input aria-label={`${t("outletHeight")} mm`} type="number" min="0" value={form.outlet_height_mm} onChange={e=>update("outlet_height_mm",number(e.target.value))}/></label>
      <label>{t("freeArea")} <span>%</span><input aria-label={`${t("freeArea")} %`} type="number" min="0" max="100" value={form.free_area_percent} onChange={e=>update("free_area_percent",e.target.value)}/></label>
    </div><p className="field-note">{t("gridNote")}</p></fieldset>
    <fieldset><legend>{t("deflectorSection")} <span className="count">{form.deflectors.length}</span></legend><div className="deflector-list">
      {form.deflectors.map((item,index)=><section className="deflector-card" key={index} aria-label={`${t("deflector")} ${index+1}`}>
        <div className="deflector-head"><input aria-label={`${t("deflector")} ${index+1} ID`} value={item.identifier} onChange={e=>updateDeflector(index,{identifier:e.target.value})}/><button type="button" onClick={()=>setForm(current=>({...current,deflectors:current.deflectors.filter((_,i)=>i!==index)}))}>{t("remove")}</button></div>
        <div className="field-grid compact">
          <label>{t("width")} <span>m</span><input aria-label={`${t("deflector")} ${index+1} ${t("width")} m`} type="number" step="0.01" value={item.width_m} onChange={e=>updateDeflector(index,{width_m:number(e.target.value)})}/></label>
          <label>{t("height")} <span>m</span><input aria-label={`${t("deflector")} ${index+1} ${t("height")} m`} type="number" step="0.01" value={item.height_m} onChange={e=>updateDeflector(index,{height_m:number(e.target.value)})}/></label>
          <label>{t("angle")} <span>deg +Y</span><input aria-label={`${t("deflector")} ${index+1} ${t("angle")}`} type="number" value={item.angle_deg_about_y} onChange={e=>updateDeflector(index,{angle_deg_about_y:number(e.target.value)})}/></label>
          {(["x","y","z"] as const).map((axis)=><label key={axis}>{t((`position${axis.toUpperCase()}`) as "positionX"|"positionY"|"positionZ")} <span>m</span><input aria-label={`${t("deflector")} ${index+1} ${axis.toUpperCase()}`} type="number" step="0.1" value={item.position_m[axis]} onChange={e=>updatePosition(index,axis,number(e.target.value))}/></label>)}
        </div></section>)}
    </div><button className="secondary full" type="button" onClick={()=>setForm(current=>({...current,deflectors:[...current.deflectors,{identifier:`D${current.deflectors.length+1}`,position_m:{x:0,y:0,z:0.075},angle_deg_about_y:45,width_m:0.2,height_m:0.2}]}))}>{t("addDeflector")}</button></fieldset>
    {errors.length>0&&<div className="error-box" role="alert"><strong>{t("checkInputs")}</strong><ul>{errors.map((item,index)=><li key={`${item.message}-${index}`}>{item.message}{item.technical&&<details><summary>{t("technicalDiagnostics")}</summary><code>{item.technical}</code></details>}</li>)}</ul></div>}
    <div className="actions"><button className="secondary" type="button" onClick={onReset}>{t("reset")}</button><button className="primary" type="button" disabled={running} onClick={onRun}>{running?t("runningSolver"):t("runSimulation")}</button></div>
  </aside>;
}
