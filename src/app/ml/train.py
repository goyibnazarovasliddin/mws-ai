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
import sys

# Add src to path so 'app' module can be imported
sys.path.append(os.path.join(os.getcwd(), 'src'))

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
        # 1. Simulate False Positives (Overlap more with TP)
        entropy = np.random.uniform(1.0, 4.2)  # Increased upper bound
        length = np.random.randint(5, 35)      # Increased upper bound
        is_test = 1 if np.random.random() > 0.3 else 0
        has_kw = 1 if np.random.random() > 0.3 else 0
        has_todo = 1 if np.random.random() > 0.5 else 0
        
        X.append([entropy, length, is_test, has_kw, has_todo])
        y.append(1)

    for _ in range(n_samples // 2):
        # 2. Simulate True Positives (Overlap more with FP)
        entropy = np.random.uniform(3.0, 6.0)  # Decreased lower bound
        length = np.random.randint(15, 60)     # Decreased lower bound
        is_test = 0
        has_kw = 0
        has_todo = 0 
        
        X.append([entropy, length, is_test, has_kw, has_todo])
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
            is_false_positive=finding.is_false_positive or False,
            confidence=finding.confidence or 0.0,
            ai_verdict=finding.ai_verdict or ""
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

import datetime

def train_model():
    """
    Main training workflow:
    1. Generates synthetic data for a strong baseline.
    2. Fetches user feedback from DB to adapt to real-world edge cases.
    3. Trains a RandomForestClassifier.
    4. Evaluates and saves the model with a unique timestamped name.
    """
    print("Step 1: Generating synthetic training data...")
    X_syn, y_syn = generate_synthetic_data()
    
    # Mix with Feedback Data from the users
    db = SessionLocal()
    try:
        print("Step 2: Checking database for user feedback...")
        X_feed, y_feed = fetch_feedback_data(db)
        if len(X_feed) > 0:
            print(f"Found {len(X_feed)} feedback records. Mixing them into the training set.")
            X = np.concatenate((X_syn, X_feed), axis=0)
            y = np.concatenate((y_syn, y_feed), axis=0)
        else:
            print("No feedback data found in DB. Training on synthetic baseline only.")
            X, y = X_syn, y_syn
    except Exception as e:
        print(f"Warning: Error fetching feedback: {e}. Falling back to synthetic only.")
        X, y = X_syn, y_syn
    finally:
        db.close()
    
    print(f"Total training samples: {X.shape[0]}")
    
    # Split for local validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and fit the classifier
    # We use a Random Forest as it handles non-linear relationships in entropy/length well.
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    
    print("Step 3: Training complete.")
    
    # Evaluate locally before saving
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred)
    print("\nLocal classification report on test partition:")
    print(report)
    
    # Step 4: Save the model
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    # 1. Save as the 'active' model for immediate app use
    joblib.dump(clf, MODEL_PATH)
    print(f"Active model updated at: {MODEL_PATH}")
    
    # 2. Save with a unique timestamped name for version tracking
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned_name = f"classifier_v_{timestamp}.pkl"
    versioned_path = os.path.join(MODEL_DIR, versioned_name)
    joblib.dump(clf, versioned_path)
    print(f"New versioned model saved as: {versioned_path}")

if __name__ == "__main__":
    train_model()

