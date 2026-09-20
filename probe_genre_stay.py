import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

url = "https://nozawakanko.jp/genre/stay/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

print(f"Status: {r.status_code}, len: {len(r.text)}")

# Find all cards/links on this genre/stay page
cards = soup.find_all("article") or soup.find_all("div", class_=re.compile(r"item|card|spot", re.I))
print(f"Found {len(cards)} cards/articles")

spot_links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/spot/" in href:
        spot_links.append((a.get_text(strip=True), href))

print(f"Total spot links: {len(spot_links)}")
for text, href in spot_links[:20]:
    if text:
        print(f"  [{text}] -> {href}")

# Check pagination
pagination = soup.select(".pagination, .nav-links, .page-numbers, a[href*='page']")
print(f"Pagination elements: {len(pagination)}")
for p in pagination:
    print("Pagination link:", p.get("href", p.text))
