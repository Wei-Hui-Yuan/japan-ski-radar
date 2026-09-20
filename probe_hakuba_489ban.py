import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json

url = "https://reserve.489ban.net/group/client/hakuba-nagano/0/plan/availabilitylist"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://reserve.489ban.net/group/client/hakuba-nagano/0/plan/availability/daily"
}
params = {"planType": "1", "fromDate": "2026-12-29"}

print("Querying Hakuba 489ban availabilitylist...")
r = requests.get(url, params=params, headers=headers, timeout=15)
print("Status:", r.status_code)
data = r.json()

page_r = requests.get("https://reserve.489ban.net/group/client/hakuba-nagano/0/plan/availability/daily", headers=headers, timeout=15)
soup = BeautifulSoup(page_r.text, "html.parser")

lodges = []
for div in soup.select(".customer-calendars"):
    cid = div.get("data-customer-id")
    parent = div.parent
    grand = parent.parent if parent else None
    name = "Unknown"
    if grand:
        # find lodge name
        title = grand.find(["h2", "h3", "h4", "p", "a"])
        if title:
            name = title.get_text(strip=True)
    lodges.append((cid, name))

print(f"Total participating lodges in Hakuba 489ban: {len(lodges)}")
for cid, name in lodges[:15]:
    print(f"  [{cid}] {name}")

# Check calendar availability
available_in_hakuba = []
if "calendars" in data:
    for cid, html in data["calendars"].items():
        if "search?date=" in html:
            # Has available date links!
            cal_soup = BeautifulSoup(html, "html.parser")
            avail_dates = [a["href"] for a in cal_soup.find_all("a", href=True)]
            available_in_hakuba.append((cid, avail_dates))

print(f"\nHakuba Lodges with ANY availability around Dec 29 - Jan 2: {len(available_in_hakuba)}")
for cid, links in available_in_hakuba:
    name = dict(lodges).get(cid, "Unknown")
    print(f"\n  Lodge: {name} (CID: {cid})")
    for l in links[:5]:
        print(f"    Available: {l}")
