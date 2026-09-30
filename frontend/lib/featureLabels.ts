// Human-readable display names for raw feature column names (see
// backend/ml/features/feature_columns.py). Falls back to a title-cased
// version of the raw name for anything not explicitly listed here.

const FEATURE_LABELS: Record<string, string> = {
  grid_position: "Grid Position",
  qualifying_gap_to_pole_seconds: "Qualifying Gap to Pole",
  driver_recent_finish_mean_3: "Recent Finish (3-race avg)",
  driver_recent_finish_mean_5: "Recent Finish (5-race avg)",
  driver_recent_grid_mean_5: "Recent Grid (5-race avg)",
  driver_recent_points_mean_5: "Recent Points (5-race avg)",
  driver_season_points_before_race: "Season Points So Far",
  driver_championship_position_before_race: "Championship Position",
  driver_circuit_avg_finish: "Circuit History (Avg Finish)",
  driver_dnf_rate_recent_10: "Recent DNF Rate (10 races)",
  driver_positions_gained_avg_5: "Positions Gained (5-race avg)",
  driver_recent_form_score: "Recent Form Score",
  driver_age_years: "Driver Age",
  constructor_recent_points_mean_5: "Constructor Recent Points",
  constructor_recent_finish_mean_5: "Constructor Recent Finish",
  constructor_dnf_rate_recent_10: "Constructor DNF Rate",
  constructor_season_points_before_race: "Constructor Season Points",
  constructor_circuit_avg_finish: "Constructor Circuit History",
  circuit_type: "Circuit Type",
};

export function featureDisplayName(rawName: string): string {
  if (FEATURE_LABELS[rawName]) return FEATURE_LABELS[rawName];
  return rawName
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
