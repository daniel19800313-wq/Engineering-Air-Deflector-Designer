import { useMemo, useState } from "react";
import type { SimulationResult } from "../../api/contracts";
import { useI18n } from "../../i18n/i18n";
import type { WorkspaceForm } from "./initialState";
import { EngineeringScene3D, type CameraView } from "./EngineeringScene3D";
import { buildEngineeringSceneModel, type HeatMetric } from "./visualizationModel";

export function GeometryPreview({ form, result }: { form: WorkspaceForm; result: SimulationResult | null }) {
  const { t } = useI18n();
  const [cameraView, setCameraView] = useState<CameraView>("isometric");
  const [metric, setMetric] = useState<HeatMetric>("airflow_percentage");
  const [showAnnotations, setShowAnnotations] = useState(true);
  const [showParticles, setShowParticles] = useState(true);
  const model = useMemo(() => buildEngineeringSceneModel(form, result, metric), [form, result, metric]);
  const views: CameraView[] = ["isometric", "front", "side", "top"];

  return <section className="panel preview-panel engineering-preview" aria-labelledby="preview-title">
    <div className="section-heading preview-heading"><div><span className="eyebrow">{t("engineering3dKicker")}</span><h2 id="preview-title">{t("engineering3dTitle")}</h2></div><span className="non-cfd-badge">{t("notCfdBadge")}</span></div>
    <div className="scene-toolbar" aria-label={t("viewControls")}>
      <div className="camera-views" role="group" aria-label={t("quickViews")}>{views.map(view => <button key={view} type="button" aria-pressed={cameraView === view} onClick={() => setCameraView(view)}>{t(`camera${view[0].toUpperCase()}${view.slice(1)}` as "cameraIsometric" | "cameraFront" | "cameraSide" | "cameraTop")}</button>)}</div>
      <label>{t("heatMetric")}<select aria-label={t("sceneHeatMetric")} value={metric} onChange={event => setMetric(event.target.value as HeatMetric)} disabled={!result}><option value="airflow_percentage">{t("airflowPercent")}</option><option value="airflow_cfm">CFM</option><option value="airflow_cmh">m³/h</option><option value="outlet_velocity_mps">m/s</option></select></label>
      <label className="scene-check"><input type="checkbox" checked={showAnnotations} onChange={event => setShowAnnotations(event.target.checked)} />{t("annotations")}</label>
      <label className="scene-check"><input type="checkbox" checked={showParticles} onChange={event => setShowParticles(event.target.checked)} disabled={!result} />{t("flowIndicators")}</label>
    </div>
    <EngineeringScene3D model={model} cameraView={cameraView} showAnnotations={showAnnotations} showParticles={showParticles} t={t} />
    <div className="scene-footer"><span>{t("cameraHelp")}</span><span>{result ? t("solverVisualActive") : t("geometryOnly")}</span></div>
  </section>;
}
