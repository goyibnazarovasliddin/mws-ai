"""
Feature extraction module.

Task:
- Extracts the necessary features for the model from the Finding (snippet, file_path and other signals):
- entropy,
- path signal (test/ mock/),
- snippet length,
- presence of placeholder words,
- regex conformity, etc.

Connection:
- Works with the finding object obtained from services/parser.py.
- Used by ml/predict.py and ml/train.py.
"""

from app.models.pydantic_schemas import FindingSchema
from app.services.rule_filter import shannon_entropy, TEST_PATHS, FALSE_POSITIVE_KEYWORDS
import numpy as np

def extract_features(finding: FindingSchema) -> np.ndarray:
    """
    Extracts a feature vector for the given finding.
    Returns a numpy array of shape (1, n_features).
    """
    secret = finding.secret_snippet or ""
    file_path = finding.file_path or ""
    
    # Feature 1: Entropy
    entropy = shannon_entropy(secret)
    
    # Feature 2: Length of secret
    length = len(secret)
    
    # Feature 3: Is test path?
    is_test_path = 1 if any(p in file_path.lower() for p in TEST_PATHS) else 0
    
    # Feature 4: Contains FP keyword?
    has_fp_keyword = 1 if any(kw in secret.lower() for kw in FALSE_POSITIVE_KEYWORDS) else 0
    
    # Feature 5: Has 'TODO' or 'FIXME' specifically? (Strong indicator)
    has_todo = 1 if "todo" in secret.lower() or "fixme" in secret.lower() else 0
    
    return np.array([[entropy, length, is_test_path, has_fp_keyword, has_todo]])

