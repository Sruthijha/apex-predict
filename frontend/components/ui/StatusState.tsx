export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-apex-gray" role="status">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-apex-red" />
      <p className="text-sm uppercase tracking-widest">{label}</p>
    </div>
  );
}

export function ErrorState({
  message = "Something went wrong.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-sm border border-apex-red/30 bg-apex-red/5 py-16 text-center">
      <p className="max-w-md text-sm text-apex-off-white/80">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-sm bg-apex-red px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white hover:bg-apex-red-dim"
        >
          Retry
        </button>
      )}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-white/10 ${className}`} />;
}
