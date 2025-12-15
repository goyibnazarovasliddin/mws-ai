
"""
Manual test script for Authentication (Register/Login).
Saves created users to 'users_created.json' for easier reference.
"""

import requests
import json
import os

API_URL = "http://localhost:8000/api/v1/auth"
# Save file in the same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users_created.json")

def save_user(username, password, email):
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except:
            pass
            
    users.append({
        "username": username,
        "password": password,
        "email": email
    })
    
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)
    print(f"User saved to {USERS_FILE}")

def run_test():
    print("--- Test 1: Register ---")
    username = input("Enter new username: ")
    password = input("Enter password: ")
    email = f"{username}@example.com"
    
    payload = {
        "username": username,
        "password": password,
        "email": email
    }
    
    try:
        res = requests.post(f"{API_URL}/register", json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
        
        if res.status_code == 200:
            save_user(username, password, email)
            
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\n--- Test 2: Login ---")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        res = requests.post(f"{API_URL}/login", data=login_data)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            token = res.json()
            print("Login SUCCESS!")
            print(f"Token Type: {token['token_type']}")
            print(f"Access Token: {token['access_token'][:20]}...")
        else:
            print("Login FAILED!")
            print(res.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_test()
