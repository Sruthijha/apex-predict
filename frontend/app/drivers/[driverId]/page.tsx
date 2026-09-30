"use client";

import { useParams } from "next/navigation";
import { useDriver, useDriverResults } from "@/hooks/useApi";
import { DriverBadge } from "@/components/ui/DriverBadge";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { TrendLineChart } from "@/components/charts/TrendLineChart";
import { circuitNameCase, ordinal } from "@/lib/format";

export default function DriverDetailPage() {
  const { driverId } = useParams<{ driverId: string }>();
  const { data: driver, isLoading, isError, refetch } = useDriver(driverId);
  const { data: results } = useDriverResults(driverId);

  if (isLoading) return <LoadingState />;
  if (isError || !driver) return <ErrorState onRetry={() => refetch()} />;

  const trend = (results ?? [])
    .slice()
    .reverse()
    .map((r) => ({ label: `R${r.round}`, value: r.position ?? 21 }));

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="flex items-center gap-5">
        <DriverBadge code={driver.code} number={driver.permanent_number} size="lg" />
        <div>
          <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">
            {driver.given_name} {driver.family_name}
          </h1>
          <p className="text-apex-off-white/70">
            {driver.nationality} {driver.current_team ? `· ${circuitNameCase(driver.current_team)}` : ""}
          </p>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-white/10 bg-white/10 sm:grid-cols-4">
        <Stat label="Season Points" value={driver.season_points.toFixed(0)} />
        <Stat label="Career Wins" value={String(driver.wins)} />
        <Stat label="Career Podiums" value={String(driver.podiums)} />
        <Stat label="Career DNFs" value={String(driver.dnfs)} />
        <Stat label="Avg. Finish" value={driver.avg_finish ? ordinal(Math.round(driver.avg_finish)) : "—"} />
        <Stat label="Avg. Qualifying" value={driver.avg_qualifying ? ordinal(Math.round(driver.avg_qualifying)) : "—"} />
      </div>

      {trend.length > 1 && (
        <div className="mt-10">
          <h2 className="mb-4 font-display text-xl font-bold uppercase">Recent Finish Trend</h2>
          <TrendLineChart data={trend} invert />
        </div>
      )}

      {results && results.length > 0 && (
        <div className="mt-10">
          <h2 className="mb-4 font-display text-xl font-bold uppercase">Recent Results</h2>
          <div className="overflow-x-auto rounded-sm border border-white/10">
            <table className="w-full text-sm">
              <thead className="bg-apex-dark-2 text-left text-xs uppercase tracking-wide text-apex-gray">
                <tr>
                  <th className="px-3 py-2">Race</th>
                  <th className="px-3 py-2">Grid</th>
                  <th className="px-3 py-2">Finish</th>
                  <th className="px-3 py-2">Points</th>
                  <th className="px-3 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr key={`${r.season}-${r.round}`} className="border-t border-white/5">
                    <td className="px-3 py-2">
                      {r.season} {r.race_name}
                    </td>
                    <td className="timing-mono px-3 py-2">{r.grid}</td>
                    <td className="timing-mono px-3 py-2">{r.position ?? "—"}</td>
                    <td className="timing-mono px-3 py-2">{r.points}</td>
                    <td className="px-3 py-2 text-apex-gray">{r.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-apex-dark-2 p-4">
      <p className="text-xs uppercase tracking-wide text-apex-gray">{label}</p>
      <p className="timing-mono mt-1 text-xl font-bold">{value}</p>
    </div>
  );
}
