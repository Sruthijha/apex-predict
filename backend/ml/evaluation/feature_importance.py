"""SHAP-based global feature importance for a trained pipeline.

Uses `shap.Explainer`, which auto-selects the appropriate exact algorithm for
the model type (LinearExplainer for linear models, TreeExplainer for tree
ensembles) rather than falling back to slow model-agnostic sampling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import shap
from sklearn.pipeline import Pipeline


def compute_feature_importance(pipeline: Pipeline, background_df: pd.DataFrame, sample_df: pd.DataFrame) -> list[dict]:
    preprocessor = pipeline.named_steps["preprocess"]
    model = pipeline.named_steps["model"]

    X_background = preprocessor.transform(background_df)
    X_sample = preprocessor.transform(sample_df)
    feature_names = preprocessor.get_feature_names_out()

    explainer = shap.Explainer(model, X_background, feature_names=feature_names)
    shap_values = explainer(X_sample)

    mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    order = np.argsort(mean_abs_shap)[::-1]

    return [
        {"feature": feature_names[i], "mean_abs_shap": float(mean_abs_shap[i])}
        for i in order
    ]
