// Mirrors backend/app/schemas/*.py. Keep in sync with the FastAPI response models.

export interface CircuitSummary {
  id: string;
  name: string;
  country: string | null;
  locality: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface HistoricalWinner {
  season: number;
  driver_id: string;
  constructor_id: string;
}

export interface CircuitDetail extends CircuitSummary {
  races_held: number;
  dnf_rate: number | null;
  historical_winners: HistoricalWinner[];
}

export interface RaceSummary {
  race_id: string;
  season: number;
  round: number;
  name: string;
  date: string;
  circuit: CircuitSummary;
  has_results: boolean;
}

export interface RaceDetail extends RaceSummary {
  has_qualifying: boolean;
}

export interface DriverSummary {
  id: string;
  code: string | null;
  permanent_number: number | null;
  given_name: string;
  family_name: string;
  nationality: string | null;
}

export interface DriverDetail extends DriverSummary {
  date_of_birth: string | null;
  current_team: string | null;
  season_points: number;
  wins: number;
  podiums: number;
  dnfs: number;
  avg_finish: number | null;
  avg_qualifying: number | null;
}

export interface RecentResult {
  season: number;
  round: number;
  race_name: string;
  circuit_id: string;
  grid: number;
  position: number | null;
  points: number;
  status: string;
}

export interface ConstructorSummary {
  id: string;
  name: string;
  nationality: string | null;
}

export interface ConstructorDetail extends ConstructorSummary {
  season_points: number;
  wins: number;
  podiums: number;
  dnf_rate: number | null;
  avg_finish: number | null;
  avg_qualifying: number | null;
  drivers: string[];
}

export type PredictionMode = "pre_weekend" | "post_qualifying";

export interface DriverExplanation {
  positive: string[];
  risk: string[];
}

export interface DriverPrediction {
  driver_id: string;
  driver_name: string;
  driver_code: string | null;
  constructor_id: string;
  constructor_name: string;
  predicted_position: number;
  win_probability: number;
  podium_probability: number;
  top5_probability: number;
  points_probability: number;
  dnf_probability: number;
  expected_points: number;
  confidence: "LOW" | "MEDIUM" | "HIGH";
  explanation: DriverExplanation;
}

export interface RacePrediction {
  race_id: string;
  season: number;
  round: number;
  prediction_mode: PredictionMode;
  model_version: string;
  generated_at: string;
  drivers: DriverPrediction[];
  used_cached_data: boolean;
}

export interface DriverSimulationOutcome {
  driver_id: string;
  driver_name: string;
  driver_code: string | null;
  win_probability: number;
  podium_probability: number;
  top5_probability: number;
  points_probability: number;
  dnf_probability: number;
  expected_finish_position: number;
  expected_points: number;
}

export interface SimulationResponse {
  race_id: string;
  n_simulations: number;
  seed: number;
  prediction_mode: PredictionMode;
  outcomes: DriverSimulationOutcome[];
  most_common_podium: string[];
}

export interface RegressionMetrics {
  mae: number;
  rmse: number;
  spearman_mean: number | null;
  kendall_mean: number | null;
  top3_overlap_mean: number | null;
  n_races: number;
}

export interface ClassificationMetrics {
  log_loss: number;
  brier_score: number;
  roc_auc: number | null;
}

export interface CalibrationPoint {
  bin_start: number;
  bin_end: number;
  predicted_mean: number;
  observed_rate: number;
  count: number;
}

export interface FeatureImportanceEntry {
  feature: string;
  importance: number;
}

export interface ModelModeMetrics {
  mode: PredictionMode;
  position_algorithm: string;
  position_test_metrics: RegressionMetrics;
  position_test_baselines: Record<string, RegressionMetrics>;
  dnf_algorithm: string;
  dnf_test_metrics: ClassificationMetrics;
  dnf_test_baseline: ClassificationMetrics;
  dnf_calibration_curve: CalibrationPoint[];
  feature_importance: FeatureImportanceEntry[];
}

export interface ModelMetricsResponse {
  trained_at: string;
  feature_version: string;
  train_seasons: string;
  validation_season: number;
  test_season: number;
  modes: ModelModeMetrics[];
}
