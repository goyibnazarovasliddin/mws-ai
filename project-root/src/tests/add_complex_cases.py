
"""
Script to add 5 complex benchmark cases with multiple findings.
Each case will have 10+ findings, mixed False Positives (FP) and True Positives (TP).
"""

import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_FILE = os.path.join(BASE_DIR, "benchmark_cases.json")

def create_complex_case(case_id, title, context_file):
    findings = []
    
    # Generate 12 findings (6 FP, 6 TP)
    
    # 1. False Positives (Low entropy, test keywords, placeholders)
    fp_snippets = [
        "pass = 'example'",
        "key = 'AKIAIOSFODNN7EXAMPLE'",
        "token = 'test-token-1'", 
        "secret = 'mock_secret'",
        "pwd = 'change_me'",
        "api_key = '00000000'"
    ]
    
    # 2. True Positives (High entropy, real-looking)
    tp_snippets = [
        "AWS_KEY = 'AKIA5B4H6J7K8L9M0N1P'",
        "sk_test_51HzU9fL7x8y9z0a1b2c3d4e5f6g7h8",
        "ghp_7z8y9x0a1b2c3d4e5f6g7h8i9j0k1l2m3n4",
        "password = 'Xy9#mP2$vL5@nQ8!'",
        "db_secret = 'e7b9c1d2-a3f4-4b5c-8d9e-0f1a2b3c4d5e'",
        "api_access = 'zaCELgL0imfnc8mVLWwsAawjYr4Rx-Af50DDqtlx'"
    ]
    
    all_snippets = fp_snippets + tp_snippets
    random.shuffle(all_snippets)
    
    for idx, snippet in enumerate(all_snippets):
        findings.append({
            "ruleId": f"complex-rule-{case_id}-{idx}",
            "message": { "text": snippet },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": { "uri": context_file },
                    "region": {
                        "startLine": 10 + idx,
                        "snippet": { "text": f"var_{idx} = {snippet}" }
                    }
                }
            }]
        })
        
    return {
        "id": case_id,
        "type": "Complex Mixed",
        "description": f"{title} (Mixed FP/TP - 12 findings)",
        "payload": {
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "gitleaks",
                        "rules": []
                    }
                },
                "results": findings
            }]
        }
    }

def main():
    if not os.path.exists(CASES_FILE):
        print("Cases file not found.")
        return

    with open(CASES_FILE, "r") as f:
        cases = json.load(f)
        
    start_id = 46
    new_cases = [
        create_complex_case(start_id, "Auth Module Chaos", "src/auth/login.py"),
        create_complex_case(start_id+1, "Config Leaks", "config/production.yaml"),
        create_complex_case(start_id+2, "Legacy Data Dump", "data/backup_2024.sql"),
        create_complex_case(start_id+3, "Frontend Build Artifacts", "build/static/js/main.chunk.js"),
        create_complex_case(start_id+4, "Test Environment Config", "tests/fixtures/secrets.json")
    ]
    
    # Remove old copies if they exist to avoid dupes
    cases = [c for c in cases if c["id"] < start_id]
    
    cases.extend(new_cases)
    
    with open(CASES_FILE, "w") as f:
        json.dump(cases, f, indent=2)
        
    print(f"Added 5 complex cases. Total cases: {len(cases)}")

if __name__ == "__main__":
    main()
