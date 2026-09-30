export function DriverBadge({
  code,
  number,
  size = "md",
}: {
  code: string | null;
  number: number | null;
  size?: "sm" | "md" | "lg";
}) {
  const dims = { sm: "h-9 w-9 text-xs", md: "h-12 w-12 text-sm", lg: "h-16 w-16 text-base" }[size];
  return (
    <div
      className={`flex ${dims} flex-col items-center justify-center rounded-sm border border-white/15 bg-apex-dark-2 font-display font-bold`}
      aria-hidden
    >
      <span className="leading-none text-apex-off-white">{code ?? "—"}</span>
      {number !== null && <span className="timing-mono text-[10px] leading-none text-apex-red">{number}</span>}
    </div>
  );
}
