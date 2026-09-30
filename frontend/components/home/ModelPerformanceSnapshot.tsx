"use client";

import { useModelMetrics } from "@/hooks/useApi";
import { Skeleton } from "@/components/ui/StatusState";

export function ModelPerformanceSnapshot() {
  const { data, isLoading } = useModelMetrics();
  const mode = data?.modes.find((m) => m.mode === "post_qualifying");

  return (
    <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Recent Model Performance</p>
      <h2 className="mb-8 font-display text-3xl font-bold uppercase">Evaluated Honestly</h2>

      {isLoading && <Skeleton className="h-32 w-full" />}

      {mode && (
        <div className="grid gap-px overflow-hidden rounded-sm border border-white/10 bg-white/10 sm:grid-cols-4">
          <Stat label="Test Season" value={String(data?.test_season)} />
          <Stat label="Position MAE" value={mode.position_test_metrics.mae.toFixed(2)} sub="positions" />
          <Stat
            label="Rank Correlation"
            value={mode.position_test_metrics.spearman_mean?.toFixed(3) ?? "—"}
            sub="Spearman"
          />
          <Stat label="DNF ROC-AUC" value={mode.dnf_test_metrics.roc_auc?.toFixed(2) ?? "—"} />
        </div>
      )}
      <p className="mt-4 max-w-2xl text-sm text-apex-off-white/70">
        These numbers come directly from a held-out test season the model never saw during training or
        tuning. The Model Lab page explains the full methodology, baselines, and where the model
        genuinely struggles.
      </p>
    </section>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-apex-dark-2 p-5">
      <p className="text-xs uppercase tracking-wide text-apex-gray">{label}</p>
      <p className="timing-mono mt-1 text-2xl font-bold">
        {value} {sub && <span className="text-xs font-normal text-apex-gray">{sub}</span>}
      </p>
    </div>
  );
}
