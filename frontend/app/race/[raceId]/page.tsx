"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import { useRace, usePrediction } from "@/hooks/useApi";
import { formatDate } from "@/lib/format";
import { TimingTower } from "@/components/race/TimingTower";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import type { PredictionMode } from "@/lib/types";

export default function RacePage() {
  const { raceId } = useParams<{ raceId: string }>();
  const [mode, setMode] = useState<PredictionMode>("post_qualifying");

  const { data: race, isLoading: raceLoading } = useRace(raceId);
  const { data: prediction, isLoading: predLoading, isError, refetch } = usePrediction(raceId, mode);

  if (raceLoading) return <LoadingState label="Loading race..." />;
  if (!race) return <ErrorState message="Race not found." />;

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">{race.circuit.country}</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">{race.name}</h1>
      <p className="mt-1 text-apex-off-white/70">{race.circuit.name}</p>

      <div className="mt-4 flex flex-wrap gap-x-6 gap-y-1 text-sm text-apex-gray">
        <span>{formatDate(race.date)}</span>
        <span>Round {race.round}</span>
        <span>Season {race.season}</span>
        {race.circuit.locality && <span>{race.circuit.locality}</span>}
      </div>

      <div className="mt-8 flex items-center justify-between">
        <h2 className="font-display text-2xl font-bold uppercase">Predicted Classification</h2>
        <div className="flex rounded-sm border border-white/15 text-xs font-semibold uppercase">
          <ModeButton active={mode === "pre_weekend"} onClick={() => setMode("pre_weekend")}>
            Pre-Weekend
          </ModeButton>
          <ModeButton active={mode === "post_qualifying"} onClick={() => setMode("post_qualifying")}>
            Post-Qualifying
          </ModeButton>
        </div>
      </div>
      {prediction && (
        <p className="mt-1 text-xs text-apex-gray">
          Showing: {prediction.prediction_mode === "post_qualifying" ? "Post-Qualifying" : "Pre-Weekend"} predictions
          {prediction.prediction_mode !== mode && " (requested mode unavailable for this race yet)"} · model{" "}
          {prediction.model_version}
        </p>
      )}

      <div className="mt-4">
        {predLoading && <LoadingState label="Analyzing grid..." />}
        {isError && (
          <ErrorState message="Predictions aren't available for this race yet." onRetry={() => refetch()} />
        )}
        {prediction && <TimingTower drivers={prediction.drivers} />}
      </div>

      <div className="mt-8 flex gap-3">
        <Link
          href={`/simulate/${race.race_id}`}
          className="rounded-sm bg-apex-red px-6 py-3 text-sm font-bold uppercase tracking-wide text-white hover:bg-apex-red-dim"
        >
          Run Race Lab Simulation
        </Link>
      </div>
    </div>
  );
}

function ModeButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-2 transition-colors ${active ? "bg-apex-red text-white" : "text-apex-gray hover:text-apex-off-white"}`}
    >
      {children}
    </button>
  );
}
