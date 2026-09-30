import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { PredictionMode } from "@/lib/types";

export const useUpcomingRace = () =>
  useQuery({ queryKey: ["races", "upcoming"], queryFn: api.upcomingRace });

export const useRaces = (season?: number) =>
  useQuery({ queryKey: ["races", season ?? "all"], queryFn: () => api.races() });

export const useRace = (raceId: string) =>
  useQuery({ queryKey: ["race", raceId], queryFn: () => api.race(raceId), enabled: !!raceId });

/** Tries post_qualifying first, falls back to pre_weekend if qualifying
 * hasn't happened yet (the API 404s in that case) - the UI clearly labels
 * whichever mode actually loaded. */
export const usePrediction = (raceId: string, preferredMode: PredictionMode) =>
  useQuery({
    queryKey: ["prediction", raceId, preferredMode],
    queryFn: async () => {
      try {
        return await api.prediction(raceId, preferredMode);
      } catch {
        if (preferredMode === "post_qualifying") {
          return api.prediction(raceId, "pre_weekend");
        }
        throw new Error("No prediction available for this race yet.");
      }
    },
    enabled: !!raceId,
  });

export const useDrivers = () => useQuery({ queryKey: ["drivers"], queryFn: api.drivers });
export const useDriver = (driverId: string) =>
  useQuery({ queryKey: ["driver", driverId], queryFn: () => api.driver(driverId), enabled: !!driverId });
export const useDriverResults = (driverId: string) =>
  useQuery({
    queryKey: ["driver-results", driverId],
    queryFn: () => api.driverResults(driverId),
    enabled: !!driverId,
  });

export const useConstructors = () => useQuery({ queryKey: ["constructors"], queryFn: api.constructors });
export const useConstructor = (constructorId: string) =>
  useQuery({
    queryKey: ["constructor", constructorId],
    queryFn: () => api.constructor(constructorId),
    enabled: !!constructorId,
  });

export const useCircuits = () => useQuery({ queryKey: ["circuits"], queryFn: api.circuits });
export const useCircuit = (circuitId: string) =>
  useQuery({ queryKey: ["circuit", circuitId], queryFn: () => api.circuit(circuitId), enabled: !!circuitId });

export const useModelMetrics = () => useQuery({ queryKey: ["model-metrics"], queryFn: api.modelMetrics });
