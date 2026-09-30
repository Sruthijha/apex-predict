"use client";

import Link from "next/link";
import { useCircuits } from "@/hooks/useApi";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";

export default function CircuitsPage() {
  const { data, isLoading, isError, refetch } = useCircuits();

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">The Calendar</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">Circuits</h1>

      {isLoading && <LoadingState />}
      {isError && <ErrorState onRetry={() => refetch()} />}

      {data && (
        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((c) => (
            <Link
              key={c.id}
              href={`/circuits/${c.id}`}
              className="rounded-sm border border-white/10 bg-apex-dark-2 p-4 transition-colors hover:border-apex-red/50"
            >
              <p className="font-display text-lg font-semibold uppercase">{c.name}</p>
              <p className="text-xs text-apex-gray">
                {c.locality}, {c.country}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
