"use client";

import { useState } from "react";
import { useDrivers, useDriver, useUpcomingRace, usePrediction } from "@/hooks/useApi";
import { DriverBadge } from "@/components/ui/DriverBadge";
import { LoadingState } from "@/components/ui/StatusState";
import { formatPercent, ordinal } from "@/lib/format";

export default function ComparePage() {
  const { data: drivers } = useDrivers();
  const [driverAId, setDriverAId] = useState("");
  const [driverBId, setDriverBId] = useState("");

  const { data: driverA } = useDriver(driverAId);
  const { data: driverB } = useDriver(driverBId);

  const { data: race } = useUpcomingRace();
  const { data: prediction } = usePrediction(race?.race_id ?? "", "post_qualifying");
  const predA = prediction?.drivers.find((d) => d.driver_id === driverAId);
  const predB = prediction?.drivers.find((d) => d.driver_id === driverBId);

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Head to Head</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">Driver Comparison</h1>

      <div className="mt-8 grid grid-cols-2 gap-4">
        <DriverSelect drivers={drivers ?? []} value={driverAId} onChange={setDriverAId} placeholder="Select driver A" />
        <DriverSelect drivers={drivers ?? []} value={driverBId} onChange={setDriverBId} placeholder="Select driver B" />
      </div>

      {driverA && driverB ? (
        <div className="mt-10">
          <div className="flex items-center justify-center gap-6">
            <div className="flex flex-col items-center gap-2">
              <DriverBadge code={driverA.code} number={driverA.permanent_number} size="lg" />
              <p className="font-display text-lg font-semibold uppercase">{driverA.family_name}</p>
            </div>
            <span className="font-display text-3xl font-bold text-apex-red">VS</span>
            <div className="flex flex-col items-center gap-2">
              <DriverBadge code={driverB.code} number={driverB.permanent_number} size="lg" />
              <p className="font-display text-lg font-semibold uppercase">{driverB.family_name}</p>
            </div>
          </div>

          <div className="mt-10 divide-y divide-white/10 rounded-sm border border-white/10">
            <CompareRow label="Season Points" a={driverA.season_points.toFixed(0)} b={driverB.season_points.toFixed(0)} />
            <CompareRow label="Career Wins" a={String(driverA.wins)} b={String(driverB.wins)} />
            <CompareRow label="Career Podiums" a={String(driverA.podiums)} b={String(driverB.podiums)} />
            <CompareRow label="Career DNFs" a={String(driverA.dnfs)} b={String(driverB.dnfs)} />
            <CompareRow
              label="Avg. Finish"
              a={driverA.avg_finish ? ordinal(Math.round(driverA.avg_finish)) : "—"}
              b={driverB.avg_finish ? ordinal(Math.round(driverB.avg_finish)) : "—"}
            />
            <CompareRow
              label="Avg. Qualifying"
              a={driverA.avg_qualifying ? ordinal(Math.round(driverA.avg_qualifying)) : "—"}
              b={driverB.avg_qualifying ? ordinal(Math.round(driverB.avg_qualifying)) : "—"}
            />
            {predA && predB && (
              <>
                <CompareRow
                  label={`Predicted Finish (${race?.name ?? "next race"})`}
                  a={predA.predicted_position.toFixed(1)}
                  b={predB.predicted_position.toFixed(1)}
                />
                <CompareRow label="Win Probability" a={formatPercent(predA.win_probability)} b={formatPercent(predB.win_probability)} />
                <CompareRow
                  label="Podium Probability"
                  a={formatPercent(predA.podium_probability)}
                  b={formatPercent(predB.podium_probability)}
                />
              </>
            )}
          </div>
        </div>
      ) : (
        <p className="mt-10 text-center text-apex-gray">Select two drivers to compare.</p>
      )}
      {(!drivers) && <LoadingState />}
    </div>
  );
}

function DriverSelect({
  drivers,
  value,
  onChange,
  placeholder,
}: {
  drivers: { id: string; given_name: string; family_name: string }[];
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-sm border border-white/15 bg-apex-dark-2 px-3 py-3 text-sm text-apex-off-white"
    >
      <option value="">{placeholder}</option>
      {drivers.map((d) => (
        <option key={d.id} value={d.id}>
          {d.given_name} {d.family_name}
        </option>
      ))}
    </select>
  );
}

function CompareRow({ label, a, b }: { label: string; a: string; b: string }) {
  return (
    <div className="grid grid-cols-3 items-center px-4 py-3 text-sm">
      <span className="timing-mono text-right font-semibold">{a}</span>
      <span className="text-center text-xs uppercase tracking-wide text-apex-gray">{label}</span>
      <span className="timing-mono text-left font-semibold">{b}</span>
    </div>
  );
}
