import requests
import json

# Test registration
url = "http://localhost:8000/auth/register"
data = {
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "testpass123"
}

try:
    response = requests.post(url, json=data)
    print(f"Registration Status Code: {response.status_code}")
    print(f"Registration Response: {response.text}")

    if response.status_code == 200:
        print("✅ Registration successful!")

        # Test login
        login_url = "http://localhost:8000/auth/login"
        login_data = {
            "username": "testuser2",
            "password": "testpass123"
        }

        login_response = requests.post(login_url, json=login_data)
        print(f"\nLogin Status Code: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")

        if login_response.status_code == 200:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
    else:
        print("❌ Registration failed!")

except Exception as e:
    print(f"Error: {e}")