import type { SimulationRequest, SimulationResult } from "./contracts";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ??
  "https://air-deflector-designer-api.onrender.com";

export class SimulationApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly technicalDetail: string,
  ) {
    super(`Simulation API returned HTTP ${status}`);
    this.name = "SimulationApiError";
  }
}

export async function runSimulation(
  request: SimulationRequest,
): Promise<SimulationResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/simulations/airflow`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null);

    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? JSON.stringify((payload as { detail: unknown }).detail)
        : response.statusText;

    throw new SimulationApiError(response.status, detail);
  }

  return response.json() as Promise<SimulationResult>;
}