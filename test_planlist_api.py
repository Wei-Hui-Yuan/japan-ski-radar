import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://reserve.489ban.net/nozawakanko/azumaya/0/planlist"
headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

r = requests.get(url, headers=headers)
print(f"Status: {r.status_code}")
try:
    data = r.json()
    print("Keys:", data.keys())
    html = data.get("planList", "")
    print(f"planList HTML length: {len(html)}")
    
    soup = BeautifulSoup(html, "html.parser")
    plans = soup.select(".c-plan-card, .plan-item, article, [class*='plan']")
    print(f"Plans found: {len(plans)}")
    
    # Extract titles and prices
    for p in soup.find_all(["div", "article"], class_=re.compile(r"plan", re.I)):
        title = p.find(["h2", "h3", "h4", "p"], class_=re.compile(r"title|name|heading", re.I))
        price = p.find(class_=re.compile(r"price|amount|yen", re.I))
        if title:
            t = title.get_text(strip=True)
            pr = price.get_text(strip=True) if price else "No price class"
            print(f"  Plan: {t[:50]} | Price: {pr}")
            
    # Also find all yen / 円 text in the HTML
    yen_texts = []
    for el in soup.find_all(text=re.compile(r'[0-9,]+円')):
        yen_texts.append(el.strip())
    print("Yen texts found:", list(set(yen_texts))[:10])
except Exception as e:
    print(f"Error parsing JSON: {e}")
    print(r.text[:500])
