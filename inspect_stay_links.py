import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

url = "https://nozawakanko.jp/stay/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

# Find all links on the stay page
print("All links on /stay/:")
for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    href = a["href"]
    if any(k in txt or k in href for k in ["泊", "宿", "ホテル", "旅館", "民宿", "ペンション", "booking", "stay", "yoyaku", "reserve", "ryokan"]):
        print(f"  {txt} -> {href}")
