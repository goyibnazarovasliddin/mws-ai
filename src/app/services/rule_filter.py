"""
Deterministic Rule-Based Filter Module.

Description:
- High-speed heuristic filter to detect obvious false positives early in the pipeline.
- Checks for file paths (e.g., test/, mock/), common placeholder keywords, and low entropy.
- Acts as the first line of defense to save resources on ML/LLM steps.

Connections:
- Used by ml_pipeline.py as the first filtering stage.
- Shared logic used by ml/features.py for feature extraction.
"""

import math
import re
from typing import Tuple

# Heuristic Keywords
# ------------------
# Tokens that strongly suggest a secret is a placeholder or example.
FALSE_POSITIVE_KEYWORDS = [
    "example", "todo", "fixme", "test", "mock", "dummy", "sample", 
    "foo", "bar", "baz", "mysqldb"
]

# Heuristic Paths
# ---------------
# File paths where secrets are likely test data or not critical.
TEST_PATHS = [
    "test/", "tests/", "mock/", "example/", "fixtures/", "venv/", "node_modules/"
]

def shannon_entropy(data: str) -> float:
    """Calculates the Shannon entropy of a string."""
    if not data:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(chr(x))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def check_is_false_positive(file_path: str, snippet: str) -> Tuple[bool, str, float]:
    """
    Checks if a finding is a False Positive based on static rules.
    Returns (is_false_positive, reason, confidence)
    """
    file_path_lower = file_path.lower()
    snippet_lower = snippet.lower()
    
    # Check 1: File Path Logic
    # ------------------------
    for path in TEST_PATHS:
        if path in file_path_lower:
            return True, f"File path contains '{path}'", 0.95
            
    # Check 2: Keyword Logic
    # ----------------------
    for kw in FALSE_POSITIVE_KEYWORDS:
        if kw in snippet_lower:
             return True, f"Snippet contains keyword '{kw}'", 0.90
             
    # Check 3: Entropy Logic
    # ----------------------
    # Secrets typically have high randomness (entropy). 
    # Low entropy usually indicates simple text like "password123" or "example".
    ent = shannon_entropy(snippet)
    if ent < 3.0 and len(snippet) > 8: # Arbitrary threshold for simple passwords
         return True, f"Low entropy ({ent:.2f}) suggests simple string/placeholder", 0.70

    return False, "Passed heuristic checks", 0.0

