import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://nozawakanko.jp/stay/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

# Find accommodation items
items = []
# Look for anchors that lead to individual stay detail pages
links = soup.find_all("a", href=True)
stay_links = []
for a in links:
    href = a["href"]
    text = a.get_text(strip=True)
    if "/spot/" in href or "/stay/" in href:
        stay_links.append((text, href))

print(f"Total links on page: {len(links)}")
print(f"Found {len(stay_links)} links with /spot/ or /stay/")

# Let's inspect page structure: tags, classes
cards = soup.select("article, .item, .c-card, .p-list__item, li")
print(f"Candidate elements: {len(cards)}")

# Let's see some sample links
sample_unique = {}
for text, href in stay_links:
    if href not in sample_unique and len(text) > 1:
        sample_unique[href] = text

for h, t in list(sample_unique.items())[:15]:
    print(f"  {t} -> {h}")
