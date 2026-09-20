import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json

# Let's test Rakuten Travel search for Nozawa Onsen:
# Rakuten Travel area code for Nozawa/Kijima/Akiyama-go:
# URL format: https://hotel.travel.rakuten.co.jp/hotelinfo/plan/...
# Or search URL: https://search.travel.rakuten.co.jp/ds/vacant/searchVacant

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

# Let's test searching Rakuten for "野沢温泉" with checkin 2026-12-29, checkout 2027-01-02, 5 adults
rakuten_search_url = "https://search.travel.rakuten.co.jp/ds/vacant/searchVacant"
params = {
    "f_query": "野沢温泉",
    "f_cd": "01",
    "f_dai": "japan",
    "f_chkin": "2026-12-29",
    "f_chkout": "2027-01-02",
    "f_adult": "5",
    "f_heya": "1"
}

try:
    r = requests.get(rakuten_search_url, params=params, headers=headers, timeout=12)
    print(f"Rakuten search status: {r.status_code}, len: {len(r.text)}")
    soup = BeautifulSoup(r.text, "html.parser")
    # Check title and hotel count
    print("Rakuten page title:", soup.title.string if soup.title else "")
    hotels = soup.select(".hotel-card, .search-result-card, [class*='hotelCard'], h2 a, h3 a")
    print(f"Hotels found on Rakuten: {len(hotels)}")
    for h in hotels[:10]:
        print(" ", h.get_text(strip=True))
except Exception as e:
    print(f"Rakuten error: {e}")
