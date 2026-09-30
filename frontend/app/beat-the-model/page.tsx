"use client";

import { useMemo, useState } from "react";
import { useRaces, useActualResults, usePrediction, useUpcomingRace } from "@/hooks/useApi";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { ReorderableGrid, type GridDriver } from "@/components/beatmodel/ReorderableGrid";
import { compareOrders, type RankingComparison } from "@/lib/rankingCompare";
import type { ActualRaceResult } from "@/lib/types";

export default function BeatTheModelPage() {
  const { data: races } = useRaces();
  const { data: upcoming } = useUpcomingRace();
  const [selectedRaceId, setSelectedRaceId] = useState<string>("");
  const raceId = selectedRaceId || upcoming?.race_id || "";

  const { data: prediction, isLoading, isError } = usePrediction(raceId, "post_qualifying");
  const { data: actual } = useActualResults(raceId);

  const modelOrder: GridDriver[] = useMemo(
    () =>
      prediction?.drivers.map((d) => ({ driver_id: d.driver_id, driver_name: d.driver_name, driver_code: d.driver_code })) ??
      [],
    [prediction],
  );

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Secret Feature</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">Beat the Model</h1>
      <p className="mt-2 max-w-2xl text-apex-off-white/70">
        Arrange the grid into your own predicted finishing order, then see how you stack up against
        the model — and, for a race that&apos;s already happened, against what actually happened.
      </p>

      <div className="mt-6">
        <label className="block text-xs uppercase tracking-wide text-apex-gray">Race</label>
        <select
          value={raceId}
          onChange={(e) => setSelectedRaceId(e.target.value)}
          className="mt-1 w-full max-w-md rounded-sm border border-white/15 bg-apex-dark-2 px-3 py-2 text-sm"
        >
          {(races ?? [])
            .slice()
            .sort((a, b) => (a.season === b.season ? b.round - a.round : b.season - a.season))
            .map((r) => (
              <option key={r.race_id} value={r.race_id}>
                {r.season} {r.name} {r.has_results ? "" : "(upcoming)"}
              </option>
            ))}
        </select>
      </div>

      {isLoading && <LoadingState label="Loading grid..." />}
      {isError && <ErrorState message="No prediction available for this race." />}

      {/* Keyed by race + model order so switching races (or the model
          finishing loading) mounts a fresh game instance with its own
          initial state, instead of reaching for an effect to reset it. */}
      {modelOrder.length > 0 && (
        <BeatTheModelGame key={raceId} modelOrder={modelOrder} actual={actual ?? null} />
      )}
    </div>
  );
}

function BeatTheModelGame({ modelOrder, actual }: { modelOrder: GridDriver[]; actual: ActualRaceResult[] | null }) {
  const [yourOrder, setYourOrder] = useState<GridDriver[]>(() =>
    [...modelOrder].sort((a, b) => a.driver_name.localeCompare(b.driver_name)),
  );
  const [lockedIn, setLockedIn] = useState(false);

  const move = (index: number, direction: -1 | 1) => {
    setYourOrder((prev) => {
      const next = [...prev];
      const target = index + direction;
      if (target < 0 || target >= next.length) return prev;
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  };

  const yourIds = yourOrder.map((d) => d.driver_id);
  const modelIds = modelOrder.map((d) => d.driver_id);
  const actualIds = actual?.map((r) => r.driver_id) ?? null;

  const vsModel = compareOrders(yourIds, modelIds);
  const vsActualYou = actualIds ? compareOrders(yourIds, actualIds) : null;
  const vsActualModel = actualIds ? compareOrders(modelIds, actualIds) : null;

  return (
    <>
      <div className="mt-8 grid gap-8 md:grid-cols-2">
        <div>
          <h2 className="mb-3 font-display text-xl font-bold uppercase">Your Grid</h2>
          <ReorderableGrid drivers={yourOrder} onMove={move} disabled={lockedIn} />
        </div>
        <div>
          <h2 className="mb-3 font-display text-xl font-bold uppercase">Model Grid</h2>
          <ReorderableGrid drivers={modelOrder} onMove={() => {}} disabled />
        </div>
      </div>

      {!lockedIn && (
        <button
          onClick={() => setLockedIn(true)}
          className="mt-8 rounded-sm bg-apex-red px-6 py-3 text-sm font-bold uppercase tracking-wide text-white hover:bg-apex-red-dim"
        >
          Lock In My Grid
        </button>
      )}

      {lockedIn && (
        <div className="mt-8 space-y-4">
          <h2 className="font-display text-xl font-bold uppercase">Results</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <ScoreCard title="You vs Model" comparison={vsModel} total={yourOrder.length} />
            {vsActualYou && <ScoreCard title="You vs Actual" comparison={vsActualYou} total={yourOrder.length} />}
            {vsActualModel && <ScoreCard title="Model vs Actual" comparison={vsActualModel} total={yourOrder.length} />}
          </div>
          {!actualIds && (
            <p className="text-xs text-apex-gray">
              This race hasn&apos;t happened yet, so there&apos;s no actual result to compare against —
              only your guess vs. the model&apos;s.
            </p>
          )}
          <button onClick={() => setLockedIn(false)} className="text-xs font-semibold text-apex-red hover:underline">
            Rearrange again
          </button>
        </div>
      )}
    </>
  );
}

function ScoreCard({ title, comparison, total }: { title: string; comparison: RankingComparison; total: number }) {
  return (
    <div className="rounded-sm border border-white/10 bg-apex-dark-2 p-4">
      <p className="font-display text-sm font-semibold uppercase text-apex-red">{title}</p>
      <dl className="mt-2 space-y-1 text-sm">
        <div className="flex justify-between">
          <dt className="text-apex-gray">Exact position matches</dt>
          <dd className="timing-mono font-semibold">
            {comparison.exactMatches} / {total}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-apex-gray">Top-3 overlap</dt>
          <dd className="timing-mono font-semibold">{comparison.top3Overlap} / 3</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-apex-gray">Avg. position difference</dt>
          <dd className="timing-mono font-semibold">{comparison.meanAbsolutePositionDiff.toFixed(1)}</dd>
        </div>
      </dl>
    </div>
  );
}
