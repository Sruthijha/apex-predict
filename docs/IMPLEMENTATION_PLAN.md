# APEX PREDICT — Implementation Plan

"Predict the race before the lights go out."

This document is the working plan for building Apex Predict, an end-to-end
Formula 1 race intelligence platform: leakage-safe ML predictions, Monte Carlo
simulation, a FastAPI backend, and a Next.js frontend. It is updated as phases
complete.

## Architecture

```mermaid
flowchart TD
    A[Jolpica-F1 API<br/>Ergast-compatible historical data] --> B[Ingestion Layer<br/>backend/ml/ingestion]
    B --> C[Raw Data Cache<br/>data/raw/*.json]
    C --> D[Preprocessing<br/>backend/ml/preprocessing]
    D --> E[Processed Tables<br/>data/processed/*.parquet]
    E --> F[Feature Engineering<br/>backend/ml/features<br/>lagged/rolling, no leakage]
    F --> G[Training Data]
    G --> H[Model Training<br/>backend/ml/training<br/>chronological split]
    H --> I[Model Artifacts<br/>data/models/*.joblib]
    I --> J[Inference Layer<br/>backend/ml/inference]
    J --> K[Monte Carlo Engine<br/>backend/ml/simulation]
    J --> L[FastAPI<br/>backend/app]
    K --> L
    L --> M[(PostgreSQL / SQLite)]
    L --> N[Next.js Frontend<br/>frontend/]
    N --> O[User]
```

## Data source decision

**Primary: Jolpica-F1** (`https://api.jolpi.ca/ergast/f1`), a free, actively
maintained, Ergast-compatible REST API covering seasons 1950–present (results,
qualifying, standings, circuits, drivers, constructors). Verified reachable
2026-09-30. No API key required. Responses are cached to `data/raw/` as JSON
so the app degrades gracefully (cached/demo mode) if the API is unreachable.

**Deferred: FastF1** (practice-session pace, telemetry, weather). Noted as
future work (see README "Future Work") — it requires large per-session
downloads and is not necessary for the core pre-race/post-qualifying
prediction targets. The ingestion layer is written with a pluggable
`SourceClient` interface so it can be added later without touching downstream
code.

## Scope decisions (engineering judgment applied per user's "make sensible
decisions yourself" instruction)

- **DB**: SQLAlchemy models written Postgres-first (JSON columns avoided,
  proper types/indexes), but local dev + CI run on SQLite for zero-setup.
  `DATABASE_URL` env var switches between them.
- **Models**: scikit-learn baselines (grid-position baseline, logistic/linear
  regression) compared against RandomForest and XGBoost. LightGBM is skipped
  as a redundant third tree library — XGBoost already demonstrates the
  tree-model comparison at this dataset size (~5-6k driver-race rows) without
  doubling maintenance surface. Deep learning is not used: tabular data this
  size gives it no evidence-based edge over calibrated tree models. Both
  trade-offs are stated explicitly on the Model Lab page, not hidden.
- **Ranking**: expected-finish regression + rank-by-score, compared against
  grid-order baseline using Spearman/Kendall/MAE/top-3 accuracy.
- **Simulation**: Monte Carlo draws per-driver finishing-position samples from
  a model-derived distribution (predicted position + residual-based spread +
  DNF draw), resolved into a valid permutation per simulated race.
- **Docker**: written and documented; not runnable in this dev environment
  (no local Docker daemon) — validated via config review + backend/frontend
  native runs instead. Flagged clearly in DEPLOYMENT.md for user verification.

## Honest results (2024 test season, models fit on 2015-2022, tuned on 2023)

These are the actual numbers from `data/models/model_registry.json` — not
illustrative placeholders. They are reported here exactly as produced,
including the parts that are not flattering, per the project's non-negotiable
"do not fabricate accuracy" rule.

| Mode | Position model | Test MAE | Test Spearman | vs. baseline |
|---|---|---|---|---|
| pre_weekend | Linear Regression | 3.31 | 0.654 | beats historical-average baseline (MAE 3.39) |
| post_qualifying | Linear Regression | 2.87 | 0.758 | **ties/slightly trails** grid-position baseline (MAE 2.83) |

| Mode | DNF model | Test LogLoss | Test Brier | Test ROC-AUC | vs. baseline |
|---|---|---|---|---|---|
| pre_weekend | Logistic Regression | 0.357 | 0.101 | 0.526 | modest lift over base-rate baseline (0.370 / 0.105) |
| post_qualifying | Logistic Regression | 0.355 | 0.101 | 0.560 | modest lift over base-rate baseline |

Two honest findings worth stating plainly rather than hiding:

1. **Linear models beat Random Forest and XGBoost** on both targets at this
   dataset size (~3,500 training driver-race rows for 2015-2022). The tree
   models' validation MAE/log-loss were consistently worse across the small
   hyperparameter grids tried. This is a legitimate, evidence-based choice,
   not a shortcut — tabular data this size with strongly linear
   grid-position/form relationships doesn't give tree ensembles room to earn
   their added variance. Reported instead of forcing a fancier-sounding
   model that measurably underperforms.
2. **Grid position alone is a very strong baseline** for post-qualifying
   finishing position (F1 drivers rarely gain or lose many places). The
   engineered model essentially ties it on raw MAE and modestly beats it on
   rank correlation (0.758 vs 0.746) and top-3 identification (0.611 vs
   lower). The real value the ML system adds over the baseline is not a
   dramatically lower MAE — it's the probabilistic, multi-output surface
   (win/podium/DNF probabilities via simulation, explanations, scenario
   analysis) that a single baseline number cannot produce at all.
3. **DNF is genuinely hard to predict** from pre-race features (ROC-AUC
   0.53-0.56, barely above chance). This matches motorsport reality:
   retirements are dominated by single-race mechanical failures and
   collisions that aren't strongly predictable from rolling historical
   stats. The model still beats the constant base-rate baseline on
   log-loss/Brier, indicating some real signal (e.g. constructor
   reliability trends), just not a strong one.

## Phases (tracking against the 20-phase spec)

- [x] Phase 1 — Inspect repo/environment
- [x] Phase 2 — Architecture & project structure
- [x] Phase 3 — Historical data ingestion (Jolpica client + cache + raw pull) — 2015-2026, 5028 driver-race rows
- [x] Phase 4 — EDA / data quality validation — fixed pagination-split bug and DNF status-classification bug
- [x] Phase 5 — Leakage-safe feature engineering — 34-column feature table, 5 leakage tests passing
- [x] Phase 6 — Baseline models (historical-average, grid-position)
- [x] Phase 7 — Stronger models (Linear/Logistic, RF, XGBoost) + small tuned grids
- [x] Phase 8 — Final model selection with evidence — see "Honest results" below
- [x] Phase 9 — Monte Carlo simulation engine + live inference + SHAP importance + explanations
- [ ] Phase 10 — FastAPI backend
- [ ] Phase 11 — Database + migrations
- [ ] Phase 12 — Frontend design system
- [ ] Phase 13 — Main frontend pages
- [ ] Phase 14 — Frontend <-> backend integration
- [ ] Phase 15 — Explainability (SHAP / rule-based factors)
- [ ] Phase 16 — Testing (backend leakage/API/sim tests, frontend smoke)
- [ ] Phase 17 — Docker
- [ ] Phase 18 — CI/CD (GitHub Actions)
- [ ] Phase 19 — Deployment prep (Vercel/Render/Neon docs)
- [ ] Phase 20 — Final audit

Progress is committed to git after each phase with a descriptive commit
message so the history itself documents the build.
