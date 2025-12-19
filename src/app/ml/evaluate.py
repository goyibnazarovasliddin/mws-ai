"""
Evaluation script for the SecretSense ML model.
This script loads the current model and calculates performance metrics.
"""

import os
import sys
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Adding project src to path so we can import 'app'
sys.path.append(os.path.join(os.getcwd(), 'src'))

from app.ml.train import generate_synthetic_data, MODEL_PATH
from app.db.session import SessionLocal
from app.ml.train import fetch_feedback_data

def evaluate_latest_model():
    """
    Loads the standard classifier.pkl and evaluates it against
    a mix of synthetic test data and real user feedback.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        print("Please run 'python -m src.app.ml.train' first.")
        return

    print(f"Loading model from: {MODEL_PATH}")
    clf = joblib.load(MODEL_PATH)

    # 1. Prepare evaluation data
    print("Preparing test data (synthetic + feedback)...")
    X_syn, y_syn = generate_synthetic_data(n_samples=200)
    
    db = SessionLocal()
    try:
        X_feed, y_feed = fetch_feedback_data(db)
    except Exception as e:
        print(f"Warning: Could not fetch feedback data: {e}")
        X_feed, y_feed = np.array([]), np.array([])
    finally:
        db.close()

    # Combine data for a more realistic test
    if len(X_feed) > 0:
        X_test = np.concatenate((X_syn, X_feed), axis=0)
        y_test = np.concatenate((y_syn, y_feed), axis=0)
    else:
        X_test, y_test = X_syn, y_syn

    # 2. Perform predictions
    y_pred = clf.predict(X_test)

    # 3. Calculate Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    # 4. Print Results
    print("\n" + "="*40)
    print(" SECRET SENSE MODEL EVALUATION RESULTS ")
    print("="*40)
    print(f"Total Test Samples : {len(y_test)}")
    print(f"Accuracy           : {acc:.4f}")
    print(f"Precision (TP)     : {prec:.4f}")
    print(f"Recall (TP)        : {rec:.4f}")
    print(f"F1-Score           : {f1:.4f}")
    print("-" * 40)
    print("Confusion Matrix:")
    print("                 Predicted TP    Predicted FP")
    print(f"Actual TP (0)      {cm[0][0]:<14} {cm[0][1]}")
    print(f"Actual FP (1)      {cm[1][0]:<14} {cm[1][1]}")
    print("="*40)

if __name__ == "__main__":
    evaluate_latest_model()
