import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse

# Search Nozawa Onsen on Rakuten
# Search URL format for Rakuten Travel
search_query = "野沢温泉"
url = f"https://search.travel.rakuten.co.jp/ds/vacant/searchVacant?f_query={urllib.parse.quote(search_query)}&f_cd=01&f_dai=japan&f_chkin=2026-12-29&f_chkout=2027-01-02&f_adult=5&f_heya=1"

r = requests.get(url, impersonate="chrome120")
print(f"Status: {r.status_code}, len: {len(r.text)}")
soup = BeautifulSoup(r.text, "html.parser")
print("Title:", soup.title.string if soup.title else "")

# Look for hotel cards
hotels = soup.select(".hotel-card, .search-card, [class*='HotelCard'], [class*='hotelItem']")
print("Hotel elements:", len(hotels))
for h in soup.find_all(["h1", "h2", "h3"]):
    t = h.get_text(strip=True)
    if "野沢" in t or "ホテル" in t or "旅館" in t or "件" in t:
        print("Heading:", t)
