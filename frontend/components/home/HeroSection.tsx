"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useUpcomingRace } from "@/hooks/useApi";
import { formatDate } from "@/lib/format";
import { Skeleton } from "@/components/ui/StatusState";

export function HeroSection() {
  const { data: race, isLoading } = useUpcomingRace();

  return (
    <section className="relative overflow-hidden border-b border-white/10 bg-apex-dark">
      <div className="checker-strip absolute inset-x-0 top-0 h-2 opacity-40" />
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:items-center lg:py-24 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <p className="mb-3 text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">
            Race Intelligence Platform
          </p>
          <h1 className="font-display text-5xl font-bold uppercase leading-[0.95] tracking-tight sm:text-6xl lg:text-7xl">
            Apex<span className="text-apex-red">Predict</span>
          </h1>
          <p className="mt-4 max-w-md text-lg text-apex-off-white/80">
            Predict the race before the lights go out.
          </p>

          {race && (
            <div className="mt-8 inline-block border-l-2 border-apex-red pl-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-apex-gray">Next Race</p>
              <p className="font-display text-2xl font-semibold">{race.name}</p>
              <p className="text-sm text-apex-off-white/70">
                {race.circuit.name} · {formatDate(race.date)}
              </p>
            </div>
          )}
          {isLoading && <Skeleton className="mt-8 h-16 w-64" />}

          <div className="mt-8 flex flex-wrap gap-3">
            {race && (
              <Link
                href={`/race/${race.race_id}`}
                className="rounded-sm bg-apex-red px-6 py-3 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-apex-red-dim"
              >
                See Predictions
              </Link>
            )}
            {race && (
              <Link
                href={`/simulate/${race.race_id}`}
                className="rounded-sm border border-white/20 px-6 py-3 text-sm font-bold uppercase tracking-wide text-apex-off-white transition-colors hover:border-white/40"
              >
                Race Lab
              </Link>
            )}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="grain-overlay flex items-center justify-center rounded-sm border border-white/10 bg-apex-dark-2 py-16"
        >
          <div className="flex gap-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <span
                key={i}
                className="h-8 w-8 rounded-full border-2 border-apex-red bg-apex-red/80 shadow-[0_0_20px_4px_rgba(225,6,0,0.5)] sm:h-10 sm:w-10"
              />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
