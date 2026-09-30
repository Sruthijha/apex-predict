"use client";

import Link from "next/link";
import { useUpcomingRace, usePrediction } from "@/hooks/useApi";
import { formatPercent } from "@/lib/format";
import { DriverBadge } from "@/components/ui/DriverBadge";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";

export function TopPredictions() {
  const { data: race } = useUpcomingRace();
  const { data: prediction, isLoading, isError, refetch } = usePrediction(
    race?.race_id ?? "",
    "post_qualifying",
  );

  return (
    <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-end justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Model&apos;s Top 3</p>
          <h2 className="font-display text-3xl font-bold uppercase">Win Probability</h2>
        </div>
        {race && (
          <Link href={`/race/${race.race_id}`} className="text-sm font-semibold text-apex-red hover:underline">
            Full grid →
          </Link>
        )}
      </div>

      {isLoading && <LoadingState label="Calculating grid..." />}
      {isError && <ErrorState message="Predictions aren't available yet for this race." onRetry={() => refetch()} />}

      {prediction && (
        <div className="grid gap-4 sm:grid-cols-3">
          {prediction.drivers.slice(0, 3).map((d, idx) => (
            <div
              key={d.driver_id}
              className="flex items-center gap-4 rounded-sm border border-white/10 bg-apex-dark-2 p-5"
            >
              <span className="font-display text-3xl font-bold text-apex-gray">{idx + 1}</span>
              <DriverBadge code={d.driver_code} number={null} />
              <div>
                <p className="font-semibold">{d.driver_name}</p>
                <p className="text-xs text-apex-gray">{d.constructor_name}</p>
                <p className="timing-mono mt-1 text-lg font-bold text-apex-red">
                  {formatPercent(d.win_probability)} <span className="text-xs text-apex-gray">WIN</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
      {prediction && (
        <p className="mt-4 text-xs text-apex-gray">
          Mode: {prediction.prediction_mode === "post_qualifying" ? "Post-Qualifying" : "Pre-Weekend"} · Model{" "}
          {prediction.model_version}
        </p>
      )}
    </section>
  );
}
