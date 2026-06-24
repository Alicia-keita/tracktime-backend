import urllib.request
import json

def test_endpoint(url, data):
    print(f"\nTesting: {url}")
    print(f"Data: {data}")
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            print("✓ SUCCESS! Status:", response.status)
            result = json.loads(response.read().decode())
            print("Response:", json.dumps(result, indent=2))
            return True
    except Exception as e:
        print("✗ FAILED!")
        print("Error:", e)
        if hasattr(e, 'read'):
            print("Error details:", e.read().decode())
        return False

print("=== TESTING LOGIN ENDPOINTS ===")

# Test 1: /api/auth/login/ with username
test_endpoint(
    'http://127.0.0.1:8000/api/auth/login/', 
    {"username": "bodiel", "password": "password123"}
)

# Test 2: /api/auth/login/ with email
test_endpoint(
    'http://127.0.0.1:8000/api/auth/login/', 
    {"email": "bodiel@gmail.com", "password": "password123"}
)

# Test 3: /api/login/ (the other endpoint)
test_endpoint(
    'http://127.0.0.1:8000/api/login/', 
    {"username": "bodiel", "password": "password123"}
)
