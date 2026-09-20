import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Search parameters
# Date: 2026-12-29
# Nights: 4
# Adults: 5 (and test with 2 rooms vs 1 room)

search_url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

params_options = [
    {"name": "5 adults, 1 room, 4 nights (2026-12-29)", "params": {"date": "2026-12-29", "numberOfNights": "4", "roomCount": "1", "adult": "5"}},
    {"name": "5 adults, 2 rooms, 4 nights (2026-12-29)", "params": {"date": "2026-12-29", "numberOfNights": "4", "roomCount": "2", "adult": "5"}},
    {"name": "2 adults, 1 room, 1 night (test general vacancy)", "params": {"date": "2026-12-29", "numberOfNights": "1", "roomCount": "1", "adult": "2"}},
    {"name": "No date specified (list all properties/plans)", "params": {"unspecifiedDate": "1"}}
]

for opt in params_options:
    print(f"\n==================== Testing: {opt['name']} ====================")
    r = requests.get(search_url, params=opt["params"], headers=headers, timeout=15)
    print(f"Request URL: {r.url}")
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Check for plan or hotel listings
    plans = soup.select(".c-plan, .plan-item, .property-item, .client-item, article, [class*='plan']")
    results_count = soup.select(".search-result__count, .count, [class*='count']")
    
    count_text = [c.get_text(strip=True) for c in results_count if c.get_text(strip=True)]
    print(f"Count text elements: {count_text}")
    print(f"Plan/property elements found: {len(plans)}")
    
    # Extract any lodge names or headings found
    headings = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3", "h4"]) if h.get_text(strip=True)]
    print(f"Headings found: {headings[:8]}")
