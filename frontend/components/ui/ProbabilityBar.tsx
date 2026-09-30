import clsx from "clsx";

export function ProbabilityBar({
  label,
  value,
  displayValue,
  accent = "red",
}: {
  label: string;
  value: number; // 0..1
  displayValue: string;
  accent?: "red" | "gray";
}) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs uppercase tracking-wide text-apex-gray">
        <span>{label}</span>
        <span className="timing-mono text-apex-off-white">{displayValue}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
        <div
          className={clsx(
            "h-full rounded-full transition-[width] duration-500",
            accent === "red" ? "bg-apex-red" : "bg-apex-gray",
          )}
          style={{ width: `${Math.min(100, Math.max(0, value * 100))}%` }}
        />
      </div>
    </div>
  );
}
