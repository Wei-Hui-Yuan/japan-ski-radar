import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://nozawakanko.jp/spot-sitemap.xml"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, "xml")

locs = [loc.text for loc in soup.find_all("loc")]
print(f"Total spots in sitemap: {len(locs)}")
print("Sample spots:")
for l in locs[:20]:
    print(" ", l)
