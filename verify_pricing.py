import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

r = requests.get('http://127.0.0.1:8000/api/lodges')
data = r.json()
print("Total lodges:", data["total"])
print("\nSample lodges with pricing:")
for l in data["data"][:6]:
    print(f"[{l['resort']}] {l['name']}")
    print(f"  Price Rate: {l.get('price_display')} {l.get('price_unit', '')}")
    print(f"  Group Est: {l.get('group_total_est')}")
    print(f"  Meal Plan: {l.get('meal_plan')}")
    print()
