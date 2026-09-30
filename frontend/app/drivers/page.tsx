"use client";

import Link from "next/link";
import { useDrivers } from "@/hooks/useApi";
import { DriverBadge } from "@/components/ui/DriverBadge";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";

export default function DriversPage() {
  const { data: drivers, isLoading, isError, refetch } = useDrivers();

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">The Grid</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">Drivers</h1>

      {isLoading && <LoadingState />}
      {isError && <ErrorState onRetry={() => refetch()} />}

      {drivers && (
        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {drivers.map((d) => (
            <Link
              key={d.id}
              href={`/drivers/${d.id}`}
              className="flex items-center gap-4 rounded-sm border border-white/10 bg-apex-dark-2 p-4 transition-colors hover:border-apex-red/50"
            >
              <DriverBadge code={d.code} number={d.permanent_number} />
              <div>
                <p className="font-semibold">
                  {d.given_name} {d.family_name}
                </p>
                <p className="text-xs text-apex-gray">{d.nationality}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
