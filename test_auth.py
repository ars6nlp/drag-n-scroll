#!/usr/bin/env python3
"""Test authentication flow"""
import requests
import json
import time

BASE_URL = "https://drag-n-scroll.onrender.com/api"

def test_registration():
    """Test user registration"""
    print("=== Testing Registration ===")
    timestamp = int(time.time())
    user_data = {
        "username": f"testuser_{timestamp}",
        "email": f"test{timestamp}@test.com",
        "password": "TestPassword123!",
        "learning_language": "RU"
    }

    response = requests.post(f"{BASE_URL}/auth/users/", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 201:
        print("[OK] Registration successful")
        return user_data["username"], user_data["password"]
    else:
        print("[FAIL] Registration failed")
        return None, None

def test_login(username, password):
    """Test user login"""
    print(f"\n=== Testing Login for {username} ===")
    login_data = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{BASE_URL}/auth/jwt/create/", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        access = data.get('access')
        refresh = data.get('refresh')

        if access and refresh:
            print("[OK] Login successful")
            print(f"Access token: {access[:50]}...")
            print(f"Refresh token: {refresh[:50]}...")
            return access
        else:
            print("[FAIL] No tokens in response")
            return None
    else:
        print("[FAIL] Login failed")
        return None

def test_get_user(access_token):
    """Test getting current user"""
    print("\n=== Testing Get Current User ===")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(f"{BASE_URL}/user/me/", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        user = response.json()
        print("[OK] Got user data:")
        print(f"  - ID: {user.get('id')}")
        print(f"  - Username: {user.get('username')}")
        print(f"  - Email: {user.get('email')}")
        print(f"  - Has profile: {bool(user.get('profile'))}")
        print(f"  - Has progress: {bool(user.get('progress'))}")

        if user.get('profile'):
            profile = user['profile']
            print(f"  Profile data:")
            print(f"    - Learning language: {profile.get('learning_language')}")
            print(f"    - HSK level: {profile.get('current_hsk_level')}")

        if user.get('progress'):
            progress = user['progress']
            print(f"  Progress data:")
            print(f"    - Current day: {progress.get('current_day')}")
            print(f"    - Total XP: {progress.get('total_xp')}")
            print(f"    - Streak days: {progress.get('streak_days')}")

        return user
    else:
        print(f"[FAIL] Failed to get user: {response.text}")
        return None

def main():
    print("Testing Authentication Flow on Render Backend\n")

    # Test registration and login
    username, password = test_registration()
    if not username:
        print("\n[WARNING]  Registration failed, trying existing user...")
        username, password = "finaltest123", "ComplexPass123!"
        # Try to create this user first
        requests.post(f"{BASE_URL}/auth/users/", json={
            "username": username,
            "email": "final@test.com",
            "password": password
        })
        time.sleep(1)

    access_token = test_login(username, password)
    if not access_token:
        print("\n[ERROR] CRITICAL: Login failed!")
        print("This is why frontend login is not working!")
        return False

    user = test_get_user(access_token)
    if not user:
        print("\n[ERROR] CRITICAL: Cannot get user after login!")
        print("This means tokens are issued but /user/me/ fails!")
        return False

    print("\n[SUCCESS] SUCCESS! Authentication flow works!")
    print(f"\nUser {username} can login and access their data.")
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
