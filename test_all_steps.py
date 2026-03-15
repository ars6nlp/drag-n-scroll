#!/usr/bin/env python3
"""Test step progression through all 5 steps"""
import requests
import json
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BACKEND_URL = "https://drag-n-scroll.onrender.com/api"

def test_all_steps():
    """Test all steps by completing them"""
    print("\n=== Testing All Steps ===")

    # Login
    login_data = {
        "username": "final_test_user",
        "password": "SecurePass456"
    }

    response = requests.post(f"{BACKEND_URL}/auth/jwt/create/", json=login_data)

    if response.status_code != 200:
        # Register
        print("Registering new user...")
        reg_data = {
            "username": "final_test_user",
            "email": "final@test.com",
            "password": "SecurePass456",
            "learning_language": "RU"
        }
        requests.post(f"{BACKEND_URL}/auth/users/", json=reg_data)
        response = requests.post(f"{BACKEND_URL}/auth/jwt/create/", json=login_data)

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
    main_screen = requests.get(
        f"{BACKEND_URL}/learning/main-screen/",
        headers=headers
    )
    data = main_screen.json()

    # Start session
    session_response = requests.post(
        f"{BACKEND_URL}/learning/start/",
        headers=headers,
        json={
            "course_day_id": data['current_course_day']['id'],
            "session_type": "A"
        }
    )
    session = session_response.json()
    session_id = session['session']['id']
    print(f"Session started: {session_id}")

    # Get initial step data (should be step 1)
    step_response = requests.get(
        f"{BACKEND_URL}/learning/step/{session_id}/",
        headers=headers
    )
    step_data = step_response.json()
    print(f"\nInitial step: {step_data['step']} - {step_data['step_type']}")
    print(f"Data keys: {list(step_data['data'].keys())}")

    # Complete step 1
    print("\n--- Completing Step 1 ---")
    step1_submit = requests.post(
        f"{BACKEND_URL}/learning/submit/step-1/",
        headers=headers,
        json={
            "session_id": session_id,
            "card_id": step_data['data']['cards'][0]['id'] if step_data['data']['cards'] else 1,
            "selected_option_id": 1,
            "current_card_index": 0,
            "total_shown_cards": 1
        }
    )
    print(f"Step 1 submit: {step1_submit.status_code}")

    # Get step 2 data
    step_response = requests.get(
        f"{BACKEND_URL}/learning/step/{session_id}/",
        headers=headers
    )
    step_data = step_response.json()
    print(f"\nAfter step 1: {step_data['step']} - {step_data['step_type']}")
    print(f"Data keys: {list(step_data['data'].keys())}")

    # Complete step 2
    print("\n--- Completing Step 2 ---")
    if step_data['data'].get('words'):
        step2_submit = requests.post(
            f"{BACKEND_URL}/learning/submit/step-2/",
            headers=headers,
            json={
                "session_id": session_id,
                "words": [{
                    "word_id": step_data['data']['words'][0]['id'],
                    "selected_option_id": 1,
                    "is_correct": True,
                    "time_spent_seconds": 5
                }]
            }
        )
        print(f"Step 2 submit: {step2_submit.status_code}")

    # Get step 3 data
    step_response = requests.get(
        f"{BACKEND_URL}/learning/step/{session_id}/",
        headers=headers
    )
    step_data = step_response.json()
    print(f"\nAfter step 2: {step_data['step']} - {step_data['step_type']}")
    print(f"Data keys: {list(step_data['data'].keys())}")

    if 'grammar_rule' in step_data['data']:
        grammar = step_data['data']['grammar_rule']
        print(f"\n[SUCCESS] Grammar rule found!")
        print(f"   Title: {grammar.get('title')}")
        print(f"   Pattern: {grammar.get('pattern')}")
        print(f"   Examples: {len(grammar.get('examples', []))}")

        if 'components' in step_data['data']:
            components = step_data['data']['components']
            print(f"\n[SUCCESS] Components found: {len(components)}")
            for comp in components:
                print(f"   - {comp.get('hanzi')} ({comp.get('pinyin')})")
    else:
        print("\n[FAIL] No grammar_rule in step 3 data!")
        print(f"Full step 3 data: {json.dumps(step_data, indent=2)}")

if __name__ == "__main__":
    test_all_steps()
