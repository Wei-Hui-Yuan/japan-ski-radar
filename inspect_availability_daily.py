import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
print(f"Status: {r.status_code}, len: {len(r.text)}")

# Look for table, calendar, dates, or JSON in scripts
tables = soup.find_all("table")
print(f"Tables: {len(tables)}")
for idx, tbl in enumerate(tables):
    rows = tbl.find_all("tr")
    print(f"Table {idx} rows: {len(rows)}")
    for r_idx, row in enumerate(rows[:5]):
        cols = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
        print(f"  Row {r_idx}: {cols[:10]}")

# Look for embedded JSON state or API calls in script tags
scripts = soup.find_all("script")
for s in scripts:
    content = s.string or ""
    if any(k in content for k in ["availability", "calendar", "rooms", "plans", "hotel", "client"]):
        print("Found matching script snippet:", content[:300])
