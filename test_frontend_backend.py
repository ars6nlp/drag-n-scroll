#!/usr/bin/env python3
"""Test frontend-backend connection"""
import requests
import json

FRONTEND_URL = "https://drag-n-scroll.vercel.app"
BACKEND_URL = "https://drag-n-scroll.onrender.com/api"

def test_cors():
    """Test CORS headers"""
    print("=== Testing CORS ===")
    response = requests.options(f"{BACKEND_URL}/auth/users/")
    print(f"OPTIONS Status: {response.status_code}")
    print(f"CORS Headers:")
    for key, value in response.headers.items():
        if 'cors' in key.lower() or 'access' in key.lower():
            print(f"  {key}: {value}")

def test_frontend_reachable():
    """Test if frontend is reachable"""
    print("\n=== Testing Frontend ===")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"Frontend Status: {response.status_code}")
        print(f"Frontend is reachable: YES")
        return True
    except Exception as e:
        print(f"Frontend Error: {e}")
        print(f"Frontend is reachable: NO")
        return False

def test_api_from_frontend():
    """Test API calls that frontend would make"""
    print("\n=== Testing API Flow ===")

    # Test 1: Registration
    print("\n1. Testing Registration...")
    reg_data = {
        "username": "frontend_test",
        "email": "frontend@test.com",
        "password": "TestPass123!",
        "learning_language": "RU"
    }
    response = requests.post(f"{BACKEND_URL}/auth/users/", json=reg_data)
    print(f"Registration Status: {response.status_code}")
    if response.status_code == 201:
        print("[OK] User created")
    elif response.status_code == 400 and 'exists' in response.text:
        print("[INFO] User already exists, continuing...")
    else:
        print(f"[FAIL] Registration failed: {response.text}")

    # Test 2: Login
    print("\n2. Testing Login...")
    login_data = {
        "username": "frontend_test",
        "password": "TestPass123!"
    }
    response = requests.post(f"{BACKEND_URL}/auth/jwt/create/", json=login_data)
    print(f"Login Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access')
        refresh_token = data.get('refresh')

        if access_token:
            print(f"[OK] Got access token: {access_token[:30]}...")
        else:
            print("[FAIL] No access token in response")
            return False

        if refresh_token:
            print(f"[OK] Got refresh token: {refresh_token[:30]}...")
        else:
            print("[FAIL] No refresh token in response")
            return False

        # Test 3: Get user
        print("\n3. Testing Get User...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BACKEND_URL}/user/me/", headers=headers)
        print(f"Get User Status: {response.status_code}")

        if response.status_code == 200:
            user = response.json()
            print(f"[OK] Got user: {user.get('username')}")
            print(f"  - Email: {user.get('email')}")
            print(f"  - Has profile: {bool(user.get('profile'))}")
            print(f"  - Has progress: {bool(user.get('progress'))}")
            return True
        else:
            print(f"[FAIL] Failed to get user: {response.text}")
            return False
    else:
        print(f"[FAIL] Login failed: {response.text}")
        return False

def main():
    print("Testing Frontend-Backend Connection\n")

    test_cors()
    test_frontend_reachable()
    success = test_api_from_frontend()

    if success:
        print("\n[SUCCESS] All tests passed!")
        print("Backend works correctly and frontend can connect.")
        print("The issue may be in frontend JavaScript code.")
    else:
        print("\n[FAIL] Some tests failed!")
        print("There is a backend or connection issue.")

if __name__ == "__main__":
    main()
