import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Check sitemap.xml
for sm_url in ["https://nozawakanko.jp/sitemap.xml", "https://nozawakanko.jp/sitemap_index.xml", "https://nozawakanko.jp/en/stay/"]:
    r = requests.get(sm_url, headers=headers, timeout=10)
    print(f"{sm_url} -> {r.status_code}, len: {len(r.text)}")
    if "sitemap" in sm_url and r.status_code == 200:
        soup = BeautifulSoup(r.text, "xml")
        locs = [loc.text for loc in soup.find_all("loc")]
        print(f"Total sitemap URLs: {len(locs)}")
        stay_locs = [l for l in locs if "spot" in l or "stay" in l]
        print(f"Spot/stay URLs in sitemap ({len(stay_locs)}):")
        for sl in stay_locs[:20]:
            print(" ", sl)
