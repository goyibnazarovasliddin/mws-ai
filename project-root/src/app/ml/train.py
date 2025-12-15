"""
Training script to train the model.

Task:
- Loads a labeled dataset (via seed_data or feedback) and performs feature extraction.
- Trains the model (LogisticRegression/RandomForest) and saves it to `ml/model/classifier.pkl`.
- Retrains the model using user feedback from the database.

Linkage:
- Uses ml/features.py for feature extraction.
- Connects to the database to fetch Feedback and Finding records.
"""

import numpy as np
import os
import joblib
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from app.db.session import SessionLocal
from app.models.db_models import Feedback, Finding
from app.ml.features import extract_features
from app.models.pydantic_schemas import FindingSchema

# Use absolute path relative to where script is run typically or fix absolute path
# We will assume this is run from project-root
MODEL_DIR = "src/app/ml/model"
MODEL_PATH = os.path.join(MODEL_DIR, "classifier.pkl")

def generate_synthetic_data(n_samples=1000):
    """
    Generates synthetic training data for secret classification.
    Features: [entropy, length, is_test_path, has_fp_keyword]
    Label: 1 (False Positive), 0 (True Positive)
    """
    X = []
    y = []

    for _ in range(n_samples // 2):
        # 1. Simulate False Positives (e.g. placeholders, test files)
        # Low entropy, short length, test paths
        entropy = np.random.uniform(1.0, 3.5)
        length = np.random.randint(5, 20)
        is_test = 1 if np.random.random() > 0.3 else 0
        has_kw = 1 if np.random.random() > 0.3 else 0
        
        # If it has strong FP signals, it's definitely FP
        X.append([entropy, length, is_test, has_kw])
        y.append(1)

    for _ in range(n_samples // 2):
        # 2. Simulate True Positives (e.g. real AWS keys, API tokens)
        # High entropy, long length, production paths
        entropy = np.random.uniform(3.8, 6.0)
        length = np.random.randint(20, 60)
        is_test = 0 # Mostly usage in prod code
        has_kw = 0 # Real keys rarely have 'example' in them
        
        X.append([entropy, length, is_test, has_kw])
        y.append(0)

    return np.array(X), np.array(y)

def fetch_feedback_data(db: Session):
    """
    Fetches confirmed feedback from the database to improve the model.
    """
    feedbacks = db.query(Feedback).join(Finding).all()
    X_feedback = []
    y_feedback = []
    
    print(f"Found {len(feedbacks)} feedback records.")
    
    for fb in feedbacks:
        finding = fb.finding
        
        # Convert DB model to Pydantic schema for feature extraction
        finding_schema = FindingSchema(
            rule_id=finding.rule_id,
            file_path=finding.file_path,
            secret_snippet=finding.secret_snippet,
            start_line=finding.start_line,
            end_line=finding.end_line
        )
        
        # Extract features
        features = extract_features(finding_schema)
        # features is shape (1, 4), we need 1D array
        X_feedback.append(features[0])
        
        # Label logic:
        # If user says is_correct=True, it means the SYSTEM's verdict was correct.
        # But we want the ground truth label (Is it a False Positive?).
        # Wait, Feedback model has: is_correct (bool) - "Was the AI verdict correct?"
        # And Finding has: is_false_positive (bool) - "What the AI thought".
        
        # If AI said "FP" (True) and User said "Correct" (True) -> Ground Truth = FP (1)
        # If AI said "TP" (False) and User said "Correct" (True) -> Ground Truth = TP (0)
        # If AI said "FP" (True) and User said "Incorrect" (False) -> Ground Truth = TP (0)
        # If AI said "TP" (False) and User said "Incorrect" (False) -> Ground Truth = FP (1)
        
        ai_verdict_fp = finding.is_false_positive
        user_confirms = fb.is_correct
        
        if user_confirms:
            ground_truth_fp = ai_verdict_fp
        else:
            ground_truth_fp = not ai_verdict_fp
            
        y_feedback.append(1 if ground_truth_fp else 0)
        
    return np.array(X_feedback), np.array(y_feedback)

def train_model():
    print("Generating synthetic training data...")
    X_syn, y_syn = generate_synthetic_data()
    
    # Mix with Feedback Data
    db = SessionLocal()
    try:
        X_feed, y_feed = fetch_feedback_data(db)
        if len(X_feed) > 0:
            print(f"Mixing in {len(X_feed)} feedback examples.")
            X = np.concatenate((X_syn, X_feed), axis=0)
            y = np.concatenate((y_syn, y_feed), axis=0)
        else:
            X, y = X_syn, y_syn
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        X, y = X_syn, y_syn
    finally:
        db.close()
    
    print(f"Total Dataset shape: {X.shape}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Simple Random Forest
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    
    print("Training complete.")
    print("Evaluation on Test Set:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Save
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
