"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useCircuit } from "@/hooks/useApi";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { formatPercent } from "@/lib/format";

export default function CircuitDetailPage() {
  const { circuitId } = useParams<{ circuitId: string }>();
  const { data: circuit, isLoading, isError, refetch } = useCircuit(circuitId);

  if (isLoading) return <LoadingState />;
  if (isError || !circuit) return <ErrorState onRetry={() => refetch()} />;

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">{circuit.country}</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">{circuit.name}</h1>
      <p className="mt-1 text-apex-off-white/70">{circuit.locality}</p>

      <div className="mt-8 grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-white/10 bg-white/10 sm:grid-cols-3">
        <Stat label="Races Held" value={String(circuit.races_held)} />
        <Stat label="DNF Rate" value={circuit.dnf_rate !== null ? formatPercent(circuit.dnf_rate) : "—"} />
        <Stat
          label="Coordinates"
          value={circuit.latitude && circuit.longitude ? `${circuit.latitude.toFixed(1)}, ${circuit.longitude.toFixed(1)}` : "—"}
        />
      </div>

      <div className="mt-10">
        <h2 className="mb-4 font-display text-xl font-bold uppercase">Historical Winners</h2>
        <div className="overflow-x-auto rounded-sm border border-white/10">
          <table className="w-full text-sm">
            <thead className="bg-apex-dark-2 text-left text-xs uppercase tracking-wide text-apex-gray">
              <tr>
                <th className="px-3 py-2">Season</th>
                <th className="px-3 py-2">Driver</th>
                <th className="px-3 py-2">Constructor</th>
              </tr>
            </thead>
            <tbody>
              {circuit.historical_winners.map((w) => (
                <tr key={w.season} className="border-t border-white/5">
                  <td className="timing-mono px-3 py-2">{w.season}</td>
                  <td className="px-3 py-2">
                    <Link href={`/drivers/${w.driver_id}`} className="hover:text-apex-red">
                      {w.driver_id.replace(/_/g, " ")}
                    </Link>
                  </td>
                  <td className="px-3 py-2">
                    <Link href={`/constructors/${w.constructor_id}`} className="hover:text-apex-red">
                      {w.constructor_id.replace(/_/g, " ")}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
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
