"use client";

import { useState } from "react";
import { useModelMetrics } from "@/hooks/useApi";
import { LoadingState, ErrorState } from "@/components/ui/StatusState";
import { ProbabilityBarChart } from "@/components/charts/ProbabilityBarChart";
import { CalibrationChart } from "@/components/charts/CalibrationChart";
import { featureDisplayName } from "@/lib/featureLabels";
import type { PredictionMode } from "@/lib/types";

export default function ModelLabPage() {
  const { data, isLoading, isError, refetch } = useModelMetrics();
  const [mode, setMode] = useState<PredictionMode>("post_qualifying");

  if (isLoading) return <LoadingState label="Loading model metrics..." />;
  if (isError || !data) return <ErrorState onRetry={() => refetch()} />;

  const modeData = data.modes.find((m) => m.mode === mode)!;

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-apex-red">Model Lab</p>
      <h1 className="font-display text-4xl font-bold uppercase sm:text-5xl">Under the Hood</h1>
      <p className="mt-4 max-w-2xl text-apex-off-white/70">
        This page reports the model&apos;s actual, honestly-measured performance on a held-out test
        season it never saw during training or hyperparameter selection. Numbers here are not
        illustrative - they come straight from the evaluation run.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-white/10 bg-white/10 sm:grid-cols-4">
        <Meta label="Train Seasons" value={data.train_seasons} />
        <Meta label="Validation Season" value={String(data.validation_season)} />
        <Meta label="Test Season" value={String(data.test_season)} />
        <Meta label="Feature Version" value={data.feature_version} />
      </div>

      <section className="mt-12">
        <h2 className="mb-4 font-display text-2xl font-bold uppercase">Targets</h2>
        <ol className="grid gap-3 text-sm sm:grid-cols-2">
          <li className="rounded-sm border border-white/10 bg-apex-dark-2 p-4">
            <strong className="text-apex-off-white">1. Finishing position</strong> — regression, ranked
            per race. Compared against a grid-position baseline.
          </li>
          <li className="rounded-sm border border-white/10 bg-apex-dark-2 p-4">
            <strong className="text-apex-off-white">2. DNF probability</strong> — calibrated binary
            classifier, compared against a constant base-rate baseline.
          </li>
          <li className="rounded-sm border border-white/10 bg-apex-dark-2 p-4 sm:col-span-2">
            <strong className="text-apex-off-white">3. Win / podium / top-5 / points probability</strong> —
            derived from Monte Carlo simulation over the position model&apos;s predicted position +
            measured residual uncertainty, and the DNF model&apos;s probability, rather than six more
            separately-trained rare-event classifiers (win rate is ~5% of driver-races - a fragile
            target to fit directly at this dataset size).
          </li>
        </ol>
      </section>

      <div className="mt-10 flex rounded-sm border border-white/15 text-xs font-semibold uppercase w-fit">
        <ModeButton active={mode === "pre_weekend"} onClick={() => setMode("pre_weekend")}>
          Pre-Weekend
        </ModeButton>
        <ModeButton active={mode === "post_qualifying"} onClick={() => setMode("post_qualifying")}>
          Post-Qualifying
        </ModeButton>
      </div>

      <section className="mt-6">
        <h2 className="mb-4 font-display text-2xl font-bold uppercase">Finishing Position Model</h2>
        <p className="mb-4 text-sm text-apex-off-white/70">
          Selected algorithm: <strong className="text-apex-off-white">{modeData.position_algorithm}</strong> — chosen
          over Random Forest and XGBoost by validation-season MAE.
        </p>
        <MetricsTable
          rows={[
            { label: modeData.position_algorithm, m: modeData.position_test_metrics },
            ...Object.entries(modeData.position_test_baselines).map(([name, m]) => ({ label: `baseline: ${name}`, m })),
          ]}
          columns={["mae", "rmse", "spearman_mean", "top3_overlap_mean"]}
        />
      </section>

      <section className="mt-12">
        <h2 className="mb-4 font-display text-2xl font-bold uppercase">DNF Risk Model</h2>
        <p className="mb-4 text-sm text-apex-off-white/70">
          Selected algorithm: <strong className="text-apex-off-white">{modeData.dnf_algorithm}</strong>, sigmoid-calibrated.
          ROC-AUC of {modeData.dnf_test_metrics.roc_auc?.toFixed(2)} reflects real difficulty — retirements are
          dominated by single-race mechanical/accident risk that isn&apos;t strongly predictable from
          pre-race form.
        </p>
        <div className="grid gap-8 lg:grid-cols-2">
          <MetricsTable
            rows={[
              { label: modeData.dnf_algorithm, m: modeData.dnf_test_metrics },
              { label: "baseline: base rate", m: modeData.dnf_test_baseline },
            ]}
            columns={["log_loss", "brier_score", "roc_auc"]}
          />
          <div>
            <p className="mb-2 text-xs uppercase tracking-wide text-apex-gray">Calibration Curve</p>
            <CalibrationChart points={modeData.dnf_calibration_curve} />
          </div>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="mb-4 font-display text-2xl font-bold uppercase">Feature Importance (SHAP)</h2>
        <ProbabilityBarChart
          data={modeData.feature_importance.slice(0, 10).map((f) => ({
            label: featureDisplayName(f.feature),
            value: f.importance / Math.max(...modeData.feature_importance.map((x) => x.importance)),
          }))}
          height={400}
          labelWidth={190}
        />
        <p className="mt-2 text-xs text-apex-gray">
          Relative mean |SHAP value|, normalized to the top feature. Feature importance reflects
          predictive association, not a causal claim.
        </p>
      </section>
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-apex-dark-2 p-4">
      <p className="text-xs uppercase tracking-wide text-apex-gray">{label}</p>
      <p className="timing-mono mt-1 text-lg font-bold">{value}</p>
    </div>
  );
}

function ModeButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick} className={`px-3 py-2 transition-colors ${active ? "bg-apex-red text-white" : "text-apex-gray hover:text-apex-off-white"}`}>
      {children}
    </button>
  );
}

function MetricsTable({
  rows,
  columns,
}: {
  rows: { label: string; m: object }[];
  columns: string[];
}) {
  return (
    <div className="overflow-x-auto rounded-sm border border-white/10">
      <table className="w-full text-sm">
        <thead className="bg-apex-dark-2 text-left text-xs uppercase tracking-wide text-apex-gray">
          <tr>
            <th className="px-3 py-2">Model</th>
            {columns.map((c) => (
              <th key={c} className="px-3 py-2">
                {c.replace(/_/g, " ")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const values = row.m as Record<string, number | null | undefined>;
            return (
              <tr key={row.label} className="border-t border-white/5">
                <td className="px-3 py-2 font-medium">{row.label}</td>
                {columns.map((c) => (
                  <td key={c} className="timing-mono px-3 py-2">
                    {values[c] !== null && values[c] !== undefined ? values[c]!.toFixed(3) : "—"}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
