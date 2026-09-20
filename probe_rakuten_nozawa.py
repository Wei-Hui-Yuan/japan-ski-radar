import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json

url = "https://travel.rakuten.co.jp/onsen/NG00455/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9"
}

r = requests.get(url, headers=headers, timeout=12)
print("Status:", r.status_code, "Len:", len(r.text))
soup = BeautifulSoup(r.text, "html.parser")

# Find hotel names on this onsen page
hotels = []
for h in soup.select("h2 a, h3 a, .hotelName a, .inn-name a"):
    name = h.get_text(strip=True)
    link = h.get("href")
    if name and "hotel" in link:
        hotels.append((name, link))

print(f"Total hotel links found: {len(hotels)}")
for n, l in hotels[:15]:
    print(f"  {n} -> {l}")
