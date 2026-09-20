import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://travel.rakuten.co.jp/"
r = requests.get(url, impersonate="chrome120")
soup = BeautifulSoup(r.text, "html.parser")

# Find search forms
forms = soup.find_all("form")
print(f"Found {len(forms)} forms")
for f in forms:
    act = f.get("action", "")
    if "search" in act or "vacant" in act or "hotel" in act:
        print("Action:", act, "Method:", f.get("method"))
        inputs = [(i.get("name"), i.get("value")) for i in f.find_all(["input", "select"]) if i.get("name")]
        print("  Inputs:", inputs[:10])
