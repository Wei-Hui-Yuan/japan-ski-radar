import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availabilitylist"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily"
}

params = {
    "planType": "1",
    "fromDate": "2026-12-29"
}

print(f"Requesting: {url} with fromDate=2026-12-29...")
r = requests.get(url, params=params, headers=headers, timeout=15)
print(f"Status: {r.status_code}")

data = r.json()
print("Keys in response:", data.keys())

# Also let's check customer list from the daily page HTML
page_r = requests.get("https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily", headers=headers, timeout=15)
soup = BeautifulSoup(page_r.text, "html.parser")

customer_divs = soup.select(".customer-calendars")
print(f"Total participating lodges on 489ban Nozawa: {len(customer_divs)}")

# Map customer IDs to lodge names
lodge_map = {}
for div in soup.select("[data-customer-id]"):
    cid = div.get("data-customer-id")
    # Find closest heading or parent card
    parent = div.find_parent("article") or div.find_parent("div", class_="c-calendar") or div.find_parent("div")
    # Look for name in parent
    name = "Unknown"
    if parent:
        name_el = parent.select_one(".c-heading, h2, h3, h4, .title, .client-name")
        if name_el:
            name = name_el.get_text(strip=True)
    lodge_map[cid] = name

print("Sample lodge mappings:", list(lodge_map.items())[:10])

# Inspect calendars in JSON
if "calendars" in data:
    calendars = data["calendars"]
    print(f"Total calendars returned: {len(calendars)}")
    
    # Parse a sample calendar HTML to see how availability is represented
    for cid, cal_html in list(calendars.items())[:5]:
        cal_soup = BeautifulSoup(cal_html, "html.parser")
        # Extract dates and symbols (e.g. ○, ×, -, 数字)
        cells = []
        for td in cal_soup.select("td, .day"):
            txt = td.get_text(strip=True)
            if txt:
                cells.append(txt)
        print(f"\nLodge ID {cid} ({lodge_map.get(cid, 'Unknown')}):")
        print(f"  Calendar cells preview: {cells[:15]}")
