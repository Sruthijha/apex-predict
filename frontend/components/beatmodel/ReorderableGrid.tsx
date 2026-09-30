"use client";

import { DriverBadge } from "@/components/ui/DriverBadge";

export interface GridDriver {
  driver_id: string;
  driver_name: string;
  driver_code: string | null;
}

export function ReorderableGrid({
  drivers,
  onMove,
  disabled = false,
}: {
  drivers: GridDriver[];
  onMove: (index: number, direction: -1 | 1) => void;
  disabled?: boolean;
}) {
  return (
    <ol className="overflow-hidden rounded-sm border border-white/10">
      {drivers.map((d, i) => (
        <li
          key={d.driver_id}
          className="flex items-center gap-3 border-b border-white/5 bg-apex-dark-2 px-3 py-2 last:border-0"
        >
          <span className="timing-mono w-8 text-sm text-apex-gray">P{i + 1}</span>
          <DriverBadge code={d.driver_code} number={null} size="sm" />
          <span className="flex-1 truncate text-sm font-medium">{d.driver_name}</span>
          {!disabled && (
            <span className="flex gap-1">
              <button
                type="button"
                aria-label={`Move ${d.driver_name} up`}
                onClick={() => onMove(i, -1)}
                disabled={i === 0}
                className="rounded-sm border border-white/15 px-2 py-1 text-xs text-apex-off-white/80 hover:border-apex-red/50 disabled:opacity-25"
              >
                ↑
              </button>
              <button
                type="button"
                aria-label={`Move ${d.driver_name} down`}
                onClick={() => onMove(i, 1)}
                disabled={i === drivers.length - 1}
                className="rounded-sm border border-white/15 px-2 py-1 text-xs text-apex-off-white/80 hover:border-apex-red/50 disabled:opacity-25"
              >
                ↓
              </button>
            </span>
          )}
        </li>
      ))}
    </ol>
  );
}
