import requests

url = "http://127.0.0.1:8000/analyze"

print("--- Testing with allowed origin (http://127.0.0.1:5173) ---")
headers_allowed = {
    "Origin": "http://127.0.0.1:5173",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type"
}
r1 = requests.options(url, headers=headers_allowed)
print(f"Status Code: {r1.status_code}")
print(f"Headers: {dict(r1.headers)}")

print("\n--- Testing with mismatched origin (http://127.0.0.1:5175) ---")
headers_mismatched = {
    "Origin": "http://127.0.0.1:5175",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type"
}
r2 = requests.options(url, headers=headers_mismatched)
print(f"Status Code: {r2.status_code}")
print(f"Headers: {dict(r2.headers)}")
print(f"Content: {r2.text}")
