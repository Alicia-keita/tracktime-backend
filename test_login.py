import requests

API_URL = 'http://127.0.0.1:8000/api/auth/login/'

# Test 1: Login with email and password
print("Test 1: Login with email bodiel@gmail.com")
response = requests.post(API_URL, json={
    "email": "bodiel@gmail.com",
    "password": "password123"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Login with username instead
print("\nTest 2: Login with username bodiel")
response = requests.post(API_URL, json={
    "username": "bodiel",
    "password": "password123"
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
