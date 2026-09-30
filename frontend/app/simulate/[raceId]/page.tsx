"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useRace } from "@/hooks/useApi";
import type { SimulationResponse } from "@/lib/types";
import { StartingLights } from "@/components/ui/StartingLights";
import { ProbabilityBarChart } from "@/components/charts/ProbabilityBarChart";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { DriverBadge } from "@/components/ui/DriverBadge";

const SIM_COUNTS = [1000, 5000, 10000];

export default function RaceLabPage() {
  const { raceId } = useParams<{ raceId: string }>();
  const { data: race } = useRace(raceId);

  const [nSimulations, setNSimulations] = useState(10000);
  const [lightsRunning, setLightsRunning] = useState(false);
  const [result, setResult] = useState<SimulationResponse | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      // Prefer post-qualifying once grid data exists; fall back to
      // pre-weekend for a race qualifying hasn't happened for yet.
      try {
        return await api.simulate(raceId, "post_qualifying", nSimulations, 42);
      } catch {
        return api.simulate(raceId, "pre_weekend", nSimulations, 42);
      }
    },
    onSuccess: (data) => setResult(data),
  });

  const handleSimulate = () => {
    setResult(null);
    setLightsRunning(true);
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Race Lab</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">Monte Carlo Simulator</h1>
      {race && <p className="mt-1 text-apex-off-white/70">{race.name}</p>}
      <p className="mt-4 max-w-2xl text-sm text-apex-off-white/70">
        Every simulated race draws each driver&apos;s finishing position from the model&apos;s predicted
        position and measured uncertainty, plus a DNF draw from the reliability model - not
        uniform randomness. Results are reproducible with a fixed seed.
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-4">
        <div className="flex rounded-sm border border-white/15 text-xs font-semibold uppercase">
          {SIM_COUNTS.map((n) => (
            <button
              key={n}
              onClick={() => setNSimulations(n)}
              className={`px-3 py-2 transition-colors ${
                nSimulations === n ? "bg-apex-red text-white" : "text-apex-gray hover:text-apex-off-white"
              }`}
            >
              {n.toLocaleString()}
            </button>
          ))}
        </div>
        <button
          onClick={handleSimulate}
          disabled={lightsRunning || mutation.isPending}
          className="rounded-sm bg-apex-red px-6 py-3 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-apex-red-dim disabled:opacity-50"
        >
          Simulate Race
        </button>
      </div>

      <div className="mt-10 flex flex-col items-center">
        <StartingLights running={lightsRunning} onLightsOut={() => {
          setLightsRunning(false);
          mutation.mutate();
        }} />
        {lightsRunning && <p className="mt-4 font-display text-lg uppercase tracking-widest text-apex-red">Lights Out</p>}
      </div>

      {mutation.isPending && <LoadingState label="Running simulations..." />}
      {mutation.isError && <ErrorState message="Couldn't run the simulation for this race." onRetry={() => mutation.mutate()} />}

      {result && (
        <div className="mt-10 space-y-12">
          <div className="text-center">
            <p className="font-display text-xl uppercase tracking-wide">
              <span className="text-apex-red">{result.n_simulations.toLocaleString()}</span> races simulated
            </p>
            <p className="mt-1 text-xs text-apex-gray">
              Mode: {result.prediction_mode === "post_qualifying" ? "Post-Qualifying" : "Pre-Weekend"} · seed {result.seed}
            </p>
          </div>

          <div className="grid gap-10 lg:grid-cols-2">
            <div>
              <h2 className="mb-4 font-display text-xl font-bold uppercase">Win Probability</h2>
              <ProbabilityBarChart
                data={result.outcomes.slice(0, 8).map((o) => ({ label: o.driver_name.split(" ").pop()!, value: o.win_probability }))}
              />
            </div>
            <div>
              <h2 className="mb-4 font-display text-xl font-bold uppercase">Podium Probability</h2>
              <ProbabilityBarChart
                data={result.outcomes
                  .slice()
                  .sort((a, b) => b.podium_probability - a.podium_probability)
                  .slice(0, 8)
                  .map((o) => ({ label: o.driver_name.split(" ").pop()!, value: o.podium_probability }))}
              />
            </div>
          </div>

          <div>
            <h2 className="mb-4 font-display text-xl font-bold uppercase">Most Common Podium</h2>
            <div className="flex flex-wrap gap-4">
              {result.most_common_podium.map((driverId, idx) => {
                const outcome = result.outcomes.find((o) => o.driver_id === driverId);
                return (
                  <div key={driverId} className="flex items-center gap-3 rounded-sm border border-white/10 bg-apex-dark-2 px-4 py-3">
                    <span className="font-display text-2xl font-bold text-apex-gray">P{idx + 1}</span>
                    <DriverBadge code={outcome?.driver_code ?? null} number={null} size="sm" />
                    <span className="text-sm font-medium">{outcome?.driver_name}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
