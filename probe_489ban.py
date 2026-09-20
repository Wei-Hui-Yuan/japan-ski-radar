import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=15)
print(f"Status: {r.status_code}, len: {len(r.text)}")

soup = BeautifulSoup(r.text, "html.parser")
print("Title:", soup.title.string if soup.title else "No title")

# Check forms, search parameters, or properties listed
forms = soup.find_all("form")
print(f"Found {len(forms)} forms")
for idx, f in enumerate(forms):
    print(f"Form {idx}: action={f.get('action')}, method={f.get('method')}")
    inputs = [i.get('name') for i in f.find_all(['input', 'select']) if i.get('name')]
    print(f"  Fields: {inputs}")

# Look for client / property links or dropdowns
clients = soup.select("select[name*='client'], .client-list, a[href*='/client/']")
print(f"Found {len(clients)} client elements")
for c in clients[:10]:
    print(" ", c.name, c.get("href") or c.get("name"))
