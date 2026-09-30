import type {
  ActualRaceResult,
  ChampionshipProjectionResponse,
  CircuitDetail,
  CircuitSummary,
  ConstructorDetail,
  ConstructorSummary,
  DriverDetail,
  DriverSummary,
  ModelMetricsResponse,
  PredictionMode,
  RaceDetail,
  RacePrediction,
  RaceSummary,
  RecentResult,
  SimulationResponse,
  WhatIfRequest,
  WhatIfResponse,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export const api = {
  races: () => apiFetch<RaceSummary[]>("/api/races"),
  upcomingRace: () => apiFetch<RaceSummary>("/api/races/upcoming"),
  race: (raceId: string) => apiFetch<RaceDetail>(`/api/races/${raceId}`),
  actualResults: (raceId: string) => apiFetch<ActualRaceResult[]>(`/api/races/${raceId}/results`),

  prediction: (raceId: string, mode: PredictionMode) =>
    apiFetch<RacePrediction>(`/api/predictions/${raceId}?mode=${mode}`),

  simulate: (raceId: string, mode: PredictionMode, nSimulations: number, seed: number) =>
    apiFetch<SimulationResponse>(`/api/simulate/${raceId}`, {
      method: "POST",
      body: JSON.stringify({ prediction_mode: mode, n_simulations: nSimulations, seed }),
    }),

  drivers: () => apiFetch<DriverSummary[]>("/api/drivers"),
  driver: (driverId: string) => apiFetch<DriverDetail>(`/api/drivers/${driverId}`),
  driverResults: (driverId: string) => apiFetch<RecentResult[]>(`/api/drivers/${driverId}/results`),

  constructors: () => apiFetch<ConstructorSummary[]>("/api/constructors"),
  constructor: (constructorId: string) => apiFetch<ConstructorDetail>(`/api/constructors/${constructorId}`),

  circuits: () => apiFetch<CircuitSummary[]>("/api/circuits"),
  circuit: (circuitId: string) => apiFetch<CircuitDetail>(`/api/circuits/${circuitId}`),

  modelMetrics: () => apiFetch<ModelMetricsResponse>("/api/model/metrics"),

  championship: (nTrials = 5000, seed = 42) =>
    apiFetch<ChampionshipProjectionResponse>(`/api/championship?n_trials=${nTrials}&seed=${seed}`),

  whatif: (raceId: string, request: WhatIfRequest) =>
    apiFetch<WhatIfResponse>(`/api/whatif/${raceId}`, {
      method: "POST",
      body: JSON.stringify(request),
    }),
};
