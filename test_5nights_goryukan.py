import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/hakuba-nagano/goryukan/0/plan/search"
headers = {"User-Agent": "Mozilla/5.0"}
params = {
    "date": "2026-12-28",
    "numberOfNights": "5",
    "roomCount": "1",
    "adult": "2"
}

r = requests.get(url, params=params, headers=headers)
print("Status:", r.status_code, "len:", len(r.text))
soup = BeautifulSoup(r.text, "html.parser")
plans = soup.select(".c-plan-card, .plan-card, .c-plan, [class*='plan']")
print("Plans count:", len(plans))
for p in plans:
    t = p.find(["h2", "h3", "h4", ".title"])
    if t:
        print("Plan:", t.get_text(strip=True))
