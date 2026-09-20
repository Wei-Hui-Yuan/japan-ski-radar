import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

url = "https://nozawakanko.jp/genre/stay/page/1/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

# Find the pagination or total page count
pages = soup.select(".page-numbers, .pagination a, a[href*='/page/']")
print("Pagination items:")
for p in pages:
    print(" ", p.get_text(strip=True), "->", p.get("href"))

# Look at articles / cards on page 1 vs page 2
def get_spots_from_page(p_num):
    u = f"https://nozawakanko.jp/genre/stay/page/{p_num}/"
    res = requests.get(u, headers=headers, timeout=10)
    sp = BeautifulSoup(res.text, "html.parser")
    titles = []
    # Find all articles or headings
    for art in sp.find_all("article"):
        h = art.find(["h2", "h3", "h4", "p"])
        a = art.find("a", href=True)
        if a:
            titles.append((h.get_text(strip=True) if h else a.get_text(strip=True), a["href"]))
    return titles

print("\nPage 1 spots:")
for t, href in get_spots_from_page(1)[:5]:
    print(f"  {t} -> {href}")

print("\nPage 2 spots:")
for t, href in get_spots_from_page(2)[:5]:
    print(f"  {t} -> {href}")
