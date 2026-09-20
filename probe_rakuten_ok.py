import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://travel.rakuten.co.jp/onsen/nagano/OK00455/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9"
}

r = requests.get(url, headers=headers, timeout=12)
print("Status:", r.status_code, "Len:", len(r.text))
soup = BeautifulSoup(r.text, "html.parser")

# Find all hotel links
hotels = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if "HOTEL/" in href.upper() and text and len(text) > 2 and text not in [h[0] for h in hotels]:
        hotels.append((text, href))

print(f"Total hotel links found: {len(hotels)}")
for n, l in hotels[:20]:
    print(f"  {n} -> {l}")
