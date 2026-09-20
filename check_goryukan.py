import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/hakuba-nagano/goryukan/0/plan/search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Test 1: 5 adults in 1 room for 4 nights
params_1 = {
    "date": "2026-12-29",
    "numberOfNights": "4",
    "roomCount": "1",
    "adult": "5"
}

# Test 2: 5 adults in 2 rooms for 4 nights (e.g. 3+2)
params_2 = {
    "date": "2026-12-29",
    "numberOfNights": "4",
    "roomCount": "2",
    "adult": "5"
}

for idx, p in enumerate([params_1, params_2], 1):
    print(f"\n--- Testing Hotel Goryukan Test {idx} (rooms: {p['roomCount']}, adults: {p['adult']}) ---")
    r = requests.get(url, params=p, headers=headers, timeout=15)
    print(f"URL: {r.url}")
    print(f"Status: {r.status_code}, len: {len(r.text)}")
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Look for plan titles and prices
    plans = soup.select(".c-plan-card, .plan-card, .c-plan, [class*='plan-box'], .plan")
    print(f"Plans found: {len(plans)}")
    
    # Extract plan titles, room names, prices
    for pl in soup.select("article, .c-plan-card, [class*='plan']"):
        title_el = pl.find(["h2", "h3", "h4", ".title", ".name"])
        price_el = pl.select_one(".price, [class*='price'], .amount")
        if title_el:
            t = title_el.get_text(strip=True)
            p_txt = price_el.get_text(strip=True) if price_el else "Price on inquiry"
            if len(t) > 3 and "ホテル五龍館" not in t:
                print(f"  Plan: {t} | {p_txt}")
