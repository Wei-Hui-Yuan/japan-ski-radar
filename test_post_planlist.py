import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://reserve.489ban.net/nozawakanko/azumaya/0/planlist"
headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://reserve.489ban.net/nozawakanko/azumaya/0/plan"
}

r = requests.post(url, headers=headers)
print(f"POST Status: {r.status_code}")
data = r.json()
print("Keys:", data.keys())
html = data.get("planList", "")
print(f"planList HTML length: {len(html)}")

soup = BeautifulSoup(html, "html.parser")
plans = soup.select(".c-plan-card, .plan-item, article, [class*='plan']")
print(f"Plans found: {len(plans)}")

for p in soup.select("article, .c-plan, [class*='plan-box'], .plan"):
    title = p.find(["h2", "h3", "h4", "p"], class_=re.compile(r"title|name|heading", re.I))
    price = p.find(class_=re.compile(r"price|amount|yen", re.I))
    if title:
        t = title.get_text(strip=True)
        pr = price.get_text(strip=True) if price else "N/A"
        print(f"  Plan: {t[:60]} | Price: {pr}")

# Find all yen strings
yen_matches = []
for el in soup.find_all(string=re.compile(r'[0-9,]+円|￥|¥')):
    txt = el.strip()
    if txt and len(txt) < 50:
        yen_matches.append(txt)

print("\nSample Yen/Price matches in planList:")
for y in list(dict.fromkeys(yen_matches))[:10]:
    print(" ", y)
