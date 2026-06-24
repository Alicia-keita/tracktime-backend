import urllib.request
import json

url = 'http://127.0.0.1:8000/api/auth/login/'

# Test 1: Login with email
print("Test 1: Login with email")
data1 = json.dumps({
    "email": "bodiel@gmail.com",
    "password": "password123"
}).encode('utf-8')

req1 = urllib.request.Request(url, data=data1, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req1) as response:
        print("Status:", response.status)
        print("Response:", json.loads(response.read().decode()))
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print("Error details:", e.read().decode())

print("\n" + "="*50 + "\n")

# Test 2: Login with username
print("Test 2: Login with username")
data2 = json.dumps({
    "username": "bodiel",
    "password": "password123"
}).encode('utf-8')

req2 = urllib.request.Request(url, data=data2, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req2) as response:
        print("Status:", response.status)
        result = json.loads(response.read().decode())
        print("Response received! Login success!")
        print("User:", result.get('user'))
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print("Error details:", e.read().decode())
