import clsx from "clsx";

const STYLES: Record<string, string> = {
  HIGH: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  MEDIUM: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  LOW: "bg-white/10 text-apex-gray border-white/20",
};

export function ConfidenceBadge({ level }: { level: string }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-sm border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider",
        STYLES[level] ?? STYLES.LOW,
      )}
    >
      {level} confidence
    </span>
  );
}
