import urllib.request
import json

def test_endpoint(url, data):
    print("\nTesting:", url)
    print("Data:", data)
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            print("SUCCESS! Status:", response.status)
            result = json.loads(response.read().decode())
            print("Response:", json.dumps(result, indent=2))
            return True
    except Exception as e:
        print("FAILED!")
        print("Error:", str(e))
        if hasattr(e, 'read'):
            try:
                print("Error details:", e.read().decode())
            except:
                pass
        return False

print("=== TESTING LOGIN ENDPOINTS ===")

test_endpoint(
    'http://127.0.0.1:8000/api/auth/login/', 
    {"username": "bodiel", "password": "password123"}
)
