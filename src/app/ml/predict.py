"""
ML Model Inference Wrapper.

Description:
- Loads the trained machine learning model (RandomForest) from the file system.
- Provides a `predict()` function that accepts feature vectors and returns classification results.
- Handles model loading errors gracefully by providing a heuristic fallback.

Connections:
- Called by ml_pipeline.py.
- Relies on the `classifier.pkl` model file.
"""

import joblib
import os
import numpy as np
from typing import Tuple

MODEL_PATH = "src/app/ml/model/classifier.pkl"
_model = None

def load_model():
    """
    Singleton pattern for loading the ML model.
    Loads once and caches in memory.
    """
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            try:
                _model = joblib.load(MODEL_PATH)
            except Exception:
                print(f"Failed to load model from {MODEL_PATH}")
                _model = "dummy"
        else:
            _model = "dummy"
    return _model

def predict(features: np.ndarray) -> Tuple[bool, float]:
    """
    Classifies a feature vector.
    Returns: (is_false_positive, probability)
    """
    model = load_model()
    
    # Fallback Logic (if no model found)
    # ----------------------------------
    if model == "dummy":
        # Simple heuristic fallback if no model
        # features: [entropy, length, is_test_path, has_fp_keyword, has_todo]
        entropy = features[0][0]
        # length = features[0][1]
        is_test_path = features[0][2]
        has_fp_keyword = features[0][3]
        
        score = 0
        if is_test_path: score += 0.8
        if has_fp_keyword: score += 0.6
        if entropy < 3.8: score += 0.6 # Increased threshold and weight to catch "password" type secrets
        
        prob = min(score, 1.0)
        return prob > 0.5, prob

    # Real Model Inference
    # --------------------
    try:
        # Assuming model has predict_proba
        prob_fp = model.predict_proba(features)[0][1] # Probability of class 1 (FP)
        return prob_fp > 0.5, float(prob_fp)
    except Exception:
        # Fallback in case of shape mismatch or other errors
        return False, 0.0

