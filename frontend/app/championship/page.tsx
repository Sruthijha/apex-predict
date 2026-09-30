"use client";

import { useChampionship } from "@/hooks/useApi";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { ProbabilityBarChart } from "@/components/charts/ProbabilityBarChart";
import { formatPercent } from "@/lib/format";

export default function ChampionshipPage() {
  const { data, isLoading, isError, refetch } = useChampionship();

  if (isLoading) return <LoadingState label="Projecting the rest of the season..." />;
  if (isError || !data) return <ErrorState onRetry={() => refetch()} />;

  const topDrivers = data.drivers.slice(0, 8);

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Championship Simulator</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">Title Fight</h1>
      <p className="mt-2 text-apex-off-white/70">
        {data.season} season · {data.remaining_races} races remaining after round {data.last_completed_round} ·{" "}
        {data.n_trials.toLocaleString()} simulated seasons
      </p>

      <div className="mt-4 rounded-sm border border-amber-500/30 bg-amber-500/5 px-4 py-3 text-xs text-amber-200/90">
        <strong className="font-semibold text-amber-200">Stated assumption:</strong> {data.assumption}
      </div>

      <section className="mt-10">
        <h2 className="mb-4 font-display text-2xl font-bold uppercase">Drivers&apos; Championship Win Probability</h2>
        <ProbabilityBarChart
          data={topDrivers.map((d) => ({ label: d.driver_name.split(" ").pop()!, value: d.championship_win_probability }))}
          height={320}
        />
      </section>

      <section className="mt-12">
        <h2 className="mb-4 font-display text-2xl font-bold uppercase">Full Driver Standings Projection</h2>
        <div className="overflow-x-auto rounded-sm border border-white/10">
          <table className="w-full text-sm">
            <thead className="bg-apex-dark-2 text-left text-xs uppercase tracking-wide text-apex-gray">
              <tr>
                <th className="px-3 py-2">Driver</th>
                <th className="px-3 py-2">Current Pts</th>
                <th className="px-3 py-2">Projected Final Pts</th>
                <th className="px-3 py-2">Title Win %</th>
                <th className="px-3 py-2">Top-3 %</th>
              </tr>
            </thead>
            <tbody>
              {data.drivers.map((d) => (
                <tr key={d.driver_id} className="border-t border-white/5">
                  <td className="px-3 py-2 font-medium">{d.driver_name}</td>
                  <td className="timing-mono px-3 py-2">{d.current_points.toFixed(0)}</td>
                  <td className="timing-mono px-3 py-2">{d.expected_final_points.toFixed(0)}</td>
                  <td className="timing-mono px-3 py-2 font-semibold text-apex-red">
                    {formatPercent(d.championship_win_probability, 1)}
                  </td>
                  <td className="timing-mono px-3 py-2">{formatPercent(d.top3_championship_probability, 1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="mb-4 font-display text-2xl font-bold uppercase">Constructors&apos; Championship Projection</h2>
        <div className="overflow-x-auto rounded-sm border border-white/10">
          <table className="w-full text-sm">
            <thead className="bg-apex-dark-2 text-left text-xs uppercase tracking-wide text-apex-gray">
              <tr>
                <th className="px-3 py-2">Constructor</th>
                <th className="px-3 py-2">Current Pts</th>
                <th className="px-3 py-2">Projected Final Pts</th>
                <th className="px-3 py-2">Title Win %</th>
              </tr>
            </thead>
            <tbody>
              {data.constructors.map((c) => (
                <tr key={c.constructor_id} className="border-t border-white/5">
                  <td className="px-3 py-2 font-medium">{c.constructor_name}</td>
                  <td className="timing-mono px-3 py-2">{c.current_points.toFixed(0)}</td>
                  <td className="timing-mono px-3 py-2">{c.expected_final_points.toFixed(0)}</td>
                  <td className="timing-mono px-3 py-2 font-semibold text-apex-red">
                    {formatPercent(c.championship_win_probability, 1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
