"""Single source of truth for which columns belong to which prediction mode.

Used by training (to select X columns), inference (to build the feature
vector for a live prediction), and to keep the two in sync so a model never
sees a different feature set at serving time than it saw at training time.
"""

FEATURE_VERSION = "v1"

CATEGORICAL_FEATURES = ["circuit_type"]

DRIVER_FEATURES = [
    "driver_recent_finish_mean_3",
    "driver_recent_finish_mean_5",
    "driver_recent_grid_mean_5",
    "driver_recent_points_mean_5",
    "driver_season_points_before_race",
    "driver_championship_position_before_race",
    "driver_circuit_avg_finish",
    "driver_dnf_rate_recent_10",
    "driver_positions_gained_avg_5",
    "driver_recent_form_score",
    "driver_age_years",
]

CONSTRUCTOR_FEATURES = [
    "constructor_recent_points_mean_5",
    "constructor_recent_finish_mean_5",
    "constructor_dnf_rate_recent_10",
    "constructor_season_points_before_race",
    "constructor_circuit_avg_finish",
]

# Available before any weekend session has run.
PRE_WEEKEND_FEATURES = DRIVER_FEATURES + CONSTRUCTOR_FEATURES + CATEGORICAL_FEATURES

# Additionally available once qualifying has taken place.
POST_QUALIFYING_ONLY_FEATURES = ["grid_position", "qualifying_gap_to_pole_seconds"]
POST_QUALIFYING_FEATURES = PRE_WEEKEND_FEATURES + POST_QUALIFYING_ONLY_FEATURES

NUMERIC_FEATURES_BY_MODE = {
    "pre_weekend": DRIVER_FEATURES + CONSTRUCTOR_FEATURES,
    "post_qualifying": DRIVER_FEATURES + CONSTRUCTOR_FEATURES + POST_QUALIFYING_ONLY_FEATURES,
}

FEATURES_BY_MODE = {
    "pre_weekend": PRE_WEEKEND_FEATURES,
    "post_qualifying": POST_QUALIFYING_FEATURES,
}
