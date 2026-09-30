"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRaces, usePrediction, useUpcomingRace } from "@/hooks/useApi";
import { api } from "@/lib/api";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { formatPercent, formatPosition } from "@/lib/format";
import type { WeatherCondition, WhatIfResponse } from "@/lib/types";

const WEATHER_OPTIONS: { value: WeatherCondition; label: string }[] = [
  { value: "dry", label: "Dry" },
  { value: "mixed", label: "Mixed" },
  { value: "wet", label: "Wet" },
];

export default function WhatIfPage() {
  const { data: races } = useRaces();
  const { data: upcoming } = useUpcomingRace();
  const [selectedRaceId, setSelectedRaceId] = useState("");
  const raceId = selectedRaceId || upcoming?.race_id || "";

  const { data: prediction } = usePrediction(raceId, "post_qualifying");

  const [weather, setWeather] = useState<WeatherCondition>("dry");
  const [gridDriverId, setGridDriverId] = useState("");
  const [newGrid, setNewGrid] = useState(1);
  const [dnfDriverId, setDnfDriverId] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      api.whatif(raceId, {
        prediction_mode: "post_qualifying",
        weather,
        grid_overrides: gridDriverId ? { [gridDriverId]: newGrid } : {},
        dnf_overrides: dnfDriverId ? { [dnfDriverId]: 1.0 } : {},
        n_simulations: 5000,
        seed: 42,
      }),
  });

  const drivers = prediction?.drivers ?? [];

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Scenario Tool</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">What If?</h1>
      <p className="mt-2 max-w-2xl text-apex-off-white/70">
        Nudge the grid, force a retirement, or change the conditions, then see how the model&apos;s
        probabilities move. A simulation, not an official forecast.
      </p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        <div>
          <label className="block text-xs uppercase tracking-wide text-apex-gray">Race</label>
          <select
            value={raceId}
            onChange={(e) => setSelectedRaceId(e.target.value)}
            className="mt-1 w-full rounded-sm border border-white/15 bg-apex-dark-2 px-3 py-2 text-sm"
          >
            {(races ?? [])
              .slice()
              .sort((a, b) => (a.season === b.season ? b.round - a.round : b.season - a.season))
              .map((r) => (
                <option key={r.race_id} value={r.race_id}>
                  {r.season} {r.name}
                </option>
              ))}
          </select>
        </div>

        <div>
          <label className="block text-xs uppercase tracking-wide text-apex-gray">Weather</label>
          <div className="mt-1 flex rounded-sm border border-white/15 text-xs font-semibold uppercase">
            {WEATHER_OPTIONS.map((w) => (
              <button
                key={w.value}
                onClick={() => setWeather(w.value)}
                className={`flex-1 px-3 py-2 transition-colors ${
                  weather === w.value ? "bg-apex-red text-white" : "text-apex-gray hover:text-apex-off-white"
                }`}
              >
                {w.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs uppercase tracking-wide text-apex-gray">Move a driver&apos;s grid slot</label>
          <div className="mt-1 flex gap-2">
            <select
              value={gridDriverId}
              onChange={(e) => setGridDriverId(e.target.value)}
              className="flex-1 rounded-sm border border-white/15 bg-apex-dark-2 px-3 py-2 text-sm"
            >
              <option value="">No change</option>
              {drivers.map((d) => (
                <option key={d.driver_id} value={d.driver_id}>
                  {d.driver_name}
                </option>
              ))}
            </select>
            <input
              type="number"
              min={1}
              max={22}
              value={newGrid}
              onChange={(e) => setNewGrid(Number(e.target.value))}
              disabled={!gridDriverId}
              className="w-20 rounded-sm border border-white/15 bg-apex-dark-2 px-3 py-2 text-sm disabled:opacity-40"
              aria-label="New grid position"
            />
          </div>
          <p className="mt-1 text-[11px] text-apex-gray">Only applies in post-qualifying mode — a real re-prediction, not a heuristic.</p>
        </div>

        <div>
          <label className="block text-xs uppercase tracking-wide text-apex-gray">Force a retirement</label>
          <select
            value={dnfDriverId}
            onChange={(e) => setDnfDriverId(e.target.value)}
            className="mt-1 w-full rounded-sm border border-white/15 bg-apex-dark-2 px-3 py-2 text-sm"
          >
            <option value="">No change</option>
            {drivers.map((d) => (
              <option key={d.driver_id} value={d.driver_id}>
                {d.driver_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={() => mutation.mutate()}
        disabled={!raceId || mutation.isPending}
        className="mt-8 rounded-sm bg-apex-red px-6 py-3 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-apex-red-dim disabled:opacity-50"
      >
        Run Scenario
      </button>

      {mutation.isPending && <LoadingState label="Re-running the model..." />}
      {mutation.isError && <ErrorState message="Couldn't build that scenario." onRetry={() => mutation.mutate()} />}
      {mutation.data && <ScenarioResults result={mutation.data} />}
    </div>
  );
}

function ScenarioResults({ result }: { result: WhatIfResponse }) {
  return (
    <div className="mt-10">
      <div className="rounded-sm border border-amber-500/30 bg-amber-500/5 px-4 py-3 text-xs text-amber-200/90">
        <p className="mb-1 font-semibold text-amber-200">
          Simulated scenario — not an official forecast ({result.prediction_mode === "post_qualifying" ? "post-qualifying" : "pre-weekend"} mode)
        </p>
        <p>{result.disclaimer}</p>
        <ul className="mt-2 list-inside list-disc">
          {result.applied_changes.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      </div>

      <div className="mt-6 overflow-x-auto rounded-sm border border-white/10">
        <table className="w-full text-sm">
          <thead className="bg-apex-dark-2 text-left text-xs uppercase tracking-wide text-apex-gray">
            <tr>
              <th className="px-3 py-2">Driver</th>
              <th className="px-3 py-2">Win (baseline → scenario)</th>
              <th className="px-3 py-2">Podium (baseline → scenario)</th>
              <th className="px-3 py-2">Expected Finish (baseline → scenario)</th>
            </tr>
          </thead>
          <tbody>
            {result.outcomes.map((o) => (
              <tr key={o.driver_id} className="border-t border-white/5">
                <td className="px-3 py-2 font-medium">{o.driver_name}</td>
                <td className="timing-mono px-3 py-2">
                  {formatPercent(o.baseline_win_probability)} → <DeltaSpan a={o.baseline_win_probability} b={o.scenario_win_probability} format={formatPercent} />
                </td>
                <td className="timing-mono px-3 py-2">
                  {formatPercent(o.baseline_podium_probability)} →{" "}
                  <DeltaSpan a={o.baseline_podium_probability} b={o.scenario_podium_probability} format={formatPercent} />
                </td>
                <td className="timing-mono px-3 py-2">
                  {formatPosition(o.baseline_expected_position)} →{" "}
                  <DeltaSpan a={o.baseline_expected_position} b={o.scenario_expected_position} format={formatPosition} higherIsBetter={false} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DeltaSpan({
  a,
  b,
  format,
  higherIsBetter = true,
}: {
  a: number;
  b: number;
  format: (v: number) => string;
  higherIsBetter?: boolean;
}) {
  const improved = higherIsBetter ? b > a : b < a;
  const worsened = higherIsBetter ? b < a : b > a;
  const color = improved ? "text-emerald-400" : worsened ? "text-apex-red" : "text-apex-off-white";
  return <span className={`font-semibold ${color}`}>{format(b)}</span>;
}
