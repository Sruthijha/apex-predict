"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { DriverPrediction } from "@/lib/types";
import { formatPercent, formatPosition } from "@/lib/format";
import { DriverBadge } from "@/components/ui/DriverBadge";
import { ConfidenceBadge } from "@/components/ui/ConfidenceBadge";

type SortKey = "predicted_position" | "win_probability" | "podium_probability" | "expected_points" | "dnf_probability";

const COLUMNS: { key: SortKey; label: string; desc?: boolean }[] = [
  { key: "predicted_position", label: "Pred." },
  { key: "win_probability", label: "Win", desc: true },
  { key: "podium_probability", label: "Podium", desc: true },
  { key: "expected_points", label: "Points", desc: true },
  { key: "dnf_probability", label: "DNF", desc: true },
];

export function TimingTower({ drivers }: { drivers: DriverPrediction[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("predicted_position");
  const [expanded, setExpanded] = useState<string | null>(null);

  const sorted = useMemo(() => {
    const col = COLUMNS.find((c) => c.key === sortKey);
    const copy = [...drivers];
    copy.sort((a, b) => (col?.desc ? b[sortKey] - a[sortKey] : a[sortKey] - b[sortKey]));
    return copy;
  }, [drivers, sortKey]);

  return (
    <div className="overflow-hidden rounded-sm border border-white/10">
      <div className="grid grid-cols-[2rem_1fr_repeat(5,4.5rem)] items-center gap-2 border-b border-white/10 bg-apex-dark-2 px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-apex-gray sm:grid-cols-[2rem_1fr_repeat(5,5rem)]">
        <span>#</span>
        <span>Driver</span>
        {COLUMNS.map((col) => (
          <button
            key={col.key}
            onClick={() => setSortKey(col.key)}
            className={`text-right transition-colors hover:text-apex-off-white ${sortKey === col.key ? "text-apex-red" : ""}`}
          >
            {col.label}
          </button>
        ))}
      </div>

      {sorted.map((d, idx) => (
        <div key={d.driver_id} className="border-b border-white/5 last:border-0">
          <button
            onClick={() => setExpanded(expanded === d.driver_id ? null : d.driver_id)}
            className="grid w-full grid-cols-[2rem_1fr_repeat(5,4.5rem)] items-center gap-2 px-3 py-2.5 text-left transition-colors hover:bg-white/5 sm:grid-cols-[2rem_1fr_repeat(5,5rem)]"
          >
            <span className="timing-mono text-sm text-apex-gray">P{idx + 1}</span>
            <span className="flex items-center gap-2 min-w-0">
              <DriverBadge code={d.driver_code} number={null} size="sm" />
              <span className="min-w-0">
                <span className="block truncate font-medium">{d.driver_name}</span>
                <span className="block truncate text-xs text-apex-gray">{d.constructor_name}</span>
              </span>
            </span>
            <span className="timing-mono text-right text-sm">{formatPosition(d.predicted_position)}</span>
            <span className="timing-mono text-right text-sm font-semibold text-apex-red">
              {formatPercent(d.win_probability)}
            </span>
            <span className="timing-mono text-right text-sm">{formatPercent(d.podium_probability)}</span>
            <span className="timing-mono text-right text-sm">{d.expected_points.toFixed(1)}</span>
            <span className="timing-mono text-right text-sm text-apex-gray">{formatPercent(d.dnf_probability)}</span>
          </button>

          {expanded === d.driver_id && (
            <div className="grid gap-4 border-t border-white/5 bg-apex-dark-2/50 px-4 py-4 sm:grid-cols-2">
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-apex-gray">Why this prediction?</p>
                <ConfidenceBadge level={d.confidence} />
                <ul className="mt-3 space-y-1 text-sm">
                  {d.explanation.positive.map((p) => (
                    <li key={p} className="text-emerald-400">
                      + {p}
                    </li>
                  ))}
                  {d.explanation.risk.map((r) => (
                    <li key={r} className="text-apex-red">
                      − {r}
                    </li>
                  ))}
                  {d.explanation.positive.length === 0 && d.explanation.risk.length === 0 && (
                    <li className="text-apex-gray">No standout factors relative to the rest of the field.</li>
                  )}
                </ul>
              </div>
              <div className="flex flex-col justify-center gap-2 text-sm">
                <Row label="Top 5 probability" value={formatPercent(d.top5_probability)} />
                <Row label="Points probability" value={formatPercent(d.points_probability)} />
                <Link
                  href={`/drivers/${d.driver_id}`}
                  className="mt-2 text-xs font-semibold text-apex-red hover:underline"
                >
                  View driver profile →
                </Link>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-white/5 pb-1">
      <span className="text-apex-gray">{label}</span>
      <span className="timing-mono font-semibold">{value}</span>
    </div>
  );
}
