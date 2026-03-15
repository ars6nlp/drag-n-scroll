#!/usr/bin/env python3
"""Test step 3, 4, 5 API responses"""
import requests
import json
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BACKEND_URL = "https://drag-n-scroll.onrender.com/api"

def test_step_3():
    """Test step 3 grammar data"""
    print("\n=== Testing Step 3: Grammar ===")

    # First, register/login
    login_data = {
        "username": "final_test_user",
        "password": "SecurePass456"
    }

    # Try to login
    response = requests.post(f"{BACKEND_URL}/auth/jwt/create/", json=login_data)

    if response.status_code != 200:
        print(f"[X] Login failed: {response.text}")
        print("Trying to register...")
        # Try to register first
        reg_data = {
            "username": "final_test_user",
            "email": "final@test.com",
            "password": "SecurePass456",
            "learning_language": "RU"
        }
        reg_response = requests.post(f"{BACKEND_URL}/auth/users/", json=reg_data)
        print(f"Register status: {reg_response.status_code}")

        if reg_response.status_code == 201:
            print("Registration successful, trying login again...")
            response = requests.post(f"{BACKEND_URL}/auth/jwt/create/", json=login_data)

    if response.status_code != 200:
        print(f"[X] Login failed: {response.text}")
        return False

    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}

    # Initialize demo course
    print("Initializing demo course...")
    init_response = requests.post(
        f"{BACKEND_URL}/learning/initialize-demo/",
        headers=headers,
        json={"hsk_level": 1}
    )
    print(f"Demo course init: {init_response.status_code}")

    # Get main screen
    print("Getting main screen...")
    main_screen = requests.get(
        f"{BACKEND_URL}/learning/main-screen/",
        headers=headers
    )

    if main_screen.status_code != 200:
        print(f"[X] Main screen failed: {main_screen.text}")
        return False

    data = main_screen.json()
    print(f"Main screen response keys: {list(data.keys())}")

    # Start session
    print("Starting session...")
    session_response = requests.post(
        f"{BACKEND_URL}/learning/start/",
        headers=headers,
        json={
            "course_day_id": data['current_course_day']['id'],
            "session_type": "A"
        }
    )

    if session_response.status_code != 200:
        print(f"[X] Start session failed: {session_response.text}")
        return False

    session = session_response.json()
    session_id = session['session']['id']
    print(f"Session started: {session_id}")

    # Get step 3 data
    print("Getting step 3 data...")
    step3_response = requests.get(
        f"{BACKEND_URL}/learning/step/{session_id}/",
        headers=headers
    )

    print(f"Step 3 status: {step3_response.status_code}")

    if step3_response.status_code == 200:
        step3_data = step3_response.json()
        print(f"\n[OK] Step 3 keys: {list(step3_data.keys())}")
        print(f"Step type: {step3_data.get('step_type')}")

        if 'data' in step3_data:
            print(f"Data keys: {list(step3_data['data'].keys())}")

            if 'grammar_rule' in step3_data['data']:
                grammar = step3_data['data']['grammar_rule']
                print(f"\n[OK] Grammar rule found:")
                print(f"   Title: {grammar.get('title')}")
                print(f"   Pattern: {grammar.get('pattern')}")
                print(f"   Examples: {len(grammar.get('examples', []))}")
            else:
                print("\n[X] No grammar_rule in data!")

            if 'components' in step3_data['data']:
                print(f"\n[OK] Components found: {len(step3_data['data']['components'])}")
                print(f"   Components: {step3_data['data']['components']}")
            else:
                print("\n[X] No components in data!")
        else:
            print("\n[X] No 'data' in step 3 response!")
            print(f"Full response: {json.dumps(step3_data, indent=2)}")
    else:
        print(f"[X] Step 3 failed: {step3_response.text}")

    return True

if __name__ == "__main__":
    test_step_3()
