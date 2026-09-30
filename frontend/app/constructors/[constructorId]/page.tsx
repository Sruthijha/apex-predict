"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useConstructor } from "@/hooks/useApi";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { formatPercent } from "@/lib/format";

export default function ConstructorDetailPage() {
  const { constructorId } = useParams<{ constructorId: string }>();
  const { data: constructor, isLoading, isError, refetch } = useConstructor(constructorId);

  if (isLoading) return <LoadingState />;
  if (isError || !constructor) return <ErrorState onRetry={() => refetch()} />;

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">{constructor.nationality}</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">{constructor.name}</h1>

      <div className="mt-8 grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-white/10 bg-white/10 sm:grid-cols-4">
        <Stat label="Season Points" value={constructor.season_points.toFixed(0)} />
        <Stat label="Career Wins" value={String(constructor.wins)} />
        <Stat label="Career Podiums" value={String(constructor.podiums)} />
        <Stat label="DNF Rate" value={constructor.dnf_rate !== null ? formatPercent(constructor.dnf_rate) : "—"} />
      </div>

      <div className="mt-10">
        <h2 className="mb-4 font-display text-xl font-bold uppercase">Drivers</h2>
        <div className="flex flex-wrap gap-3">
          {constructor.drivers.map((driverId) => (
            <Link
              key={driverId}
              href={`/drivers/${driverId}`}
              className="rounded-sm border border-white/10 bg-apex-dark-2 px-4 py-2 text-sm hover:border-apex-red/50"
            >
              {driverId.replace(/_/g, " ")}
            </Link>
          ))}
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
