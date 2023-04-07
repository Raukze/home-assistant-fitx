import sys
import requests

r = requests.get("https://mein.fitx.de/nox/public/v1/studios", headers={"x-tenant": "fitx"})

if not r.status_code == 200:
    print(f"ERROR: Unsuccessful request. HTTP Status Code: ${r.status_code}")
    sys.exit()

items = r.json()
for item in items:
    print(f"{item['name']},{item['id']}")