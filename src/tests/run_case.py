"""
Run a specific benchmark case by ID.
"""


import requests
import json
import argparse
import sys

API_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "12345678"
import os
CASES_FILE = os.path.join("src", "tests", "benchmark_cases.json")

def get_auth_token():
    try:
        requests.post(f"{API_URL}/auth/register", json={"username": USERNAME, "password": PASSWORD, "email": "test@example.com"})
    except:
        pass 
    
    res = requests.post(f"{API_URL}/auth/login", data={"username": USERNAME, "password": PASSWORD})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        sys.exit(1)
    return res.json()["access_token"]

def main():
    parser = argparse.ArgumentParser(description="Run a specific benchmark case by ID")
    parser.add_argument("id", type=int, help="ID of the test case to run (1-45)")
    args = parser.parse_args()

    # 1. Load cases
    try:
        with open(CASES_FILE, "r") as f:
            cases = json.load(f)
    except FileNotFoundError:
        print(f"Error: {CASES_FILE} not found.")
        return

    # 2. Find case
    target_case = next((c for c in cases if c["id"] == args.id), None)
    if not target_case:
        print(f"Error: Case ID {args.id} not found.")
        return

    print(f"Running Case #{target_case['id']} (Expected Type: {target_case['type']})...")

    # 3. Authenticate
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Analyze
    payload = {
        "tool": "sarif",
        "report": target_case["payload"]
    }
    
    try:
        res = requests.post(f"{API_URL}/analyze", json=payload, headers=headers)
        if res.status_code != 200:
            print(f"Analysis Error: {res.text}")
            return
        report_id = res.json()["report_id"]
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    # 5. Get Results
    res_results = requests.get(f"{API_URL}/results/{report_id}", headers=headers)
    final_results = res_results.json()

    # 6. Format Output & Interactive Feedback
    findings = final_results.get("findings", [])
    
    print(f"\n--- Analysis Complete: {len(findings)} Findings Detected ---")
    
    if not findings:
        print("No findings to review.")
        return

    # iterate through findings
    for idx, f in enumerate(findings):
        print(f"\n[{idx+1}/{len(findings)}] Finding ID: {f.get('id', 'N/A')}")
        print(f"   Rule: {f['rule_id']}")
        print(f"   File: {f['file_path']}")
        print(f"   Snippet: {f['secret_snippet']}")
        print(f"   Confidence: {f['confidence']}")
        print(f"   AI Verdict: {'False Positive (Safe)' if f['is_false_positive'] else 'True Positive (SECRET!)'}")
        print(f"   AI Reason: {f.get('ai_verdict', '')}")
        
        # User Feedback Loop
        while True:
            choice = input("   >> Is this a False Positive? (1=Yes, 0=No, s=Skip): ").strip().lower()
            if choice == 's':
                print("   Skipped.")
                break
            
            if choice in ['1', '0']:
                user_says_fp = (choice == '1')
                ai_says_fp = f['is_false_positive']
                
                # Logic: If user agrees with AI -> Correct. If not -> Incorrect.
                # AI says FP (True), User says FP (True) -> Correct
                # AI says TP (False), User says FP (True) -> Incorrect
                is_correct = (user_says_fp == ai_says_fp)
                
                # Construct Comment
                user_label = "False Positive" if user_says_fp else "True Positive"
                comment = f"User explicitly marked as {user_label}"
                
                feedback_payload = {
                    "finding_id": f['id'],
                    "is_correct": is_correct,
                    "comment": comment
                }
                
                try:
                    fb_res = requests.post(f"{API_URL}/feedback/", json=feedback_payload, headers=headers)
                    if fb_res.status_code == 200:
                        print("   Feedback Saved! (System will learn)")
                    else:
                        print(f"   Error saving feedback: {fb_res.text}")
                except Exception as e:
                    print(f"   Connection error: {e}")
                
                break
            else:
                print("   Invalid input. Please enter 1, 0, or s.")

    print("\nDone reviewing all findings.")

if __name__ == "__main__":
    main()
