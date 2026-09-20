import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

page_url = "https://reserve.489ban.net/nozawakanko/azumaya/0/plan"
r_page = session.get(page_url)
soup_page = BeautifulSoup(r_page.text, "html.parser")

# Extract CSRF token
csrf_meta = soup_page.select_one("meta[name='csrf-token']")
csrf_token = csrf_meta.get("content") if csrf_meta else None
print("CSRF Token:", csrf_token)

post_headers = {
    "X-CSRF-TOKEN": csrf_token,
    "X-Requested-With": "XMLHttpRequest",
    "Referer": page_url
}

api_url = "https://reserve.489ban.net/nozawakanko/azumaya/0/planlist"
r_post = session.post(api_url, headers=post_headers)
print(f"POST Status: {r_post.status_code}")
data = r_post.json()
print("Keys:", data.keys())

plan_html = data.get("planList", "")
print(f"planList HTML len: {len(plan_html)}")

soup = BeautifulSoup(plan_html, "html.parser")
plans = soup.select(".c-plan-card, .plan-item, article, [class*='plan']")
print(f"Plans found: {len(plans)}")

# Find all yen or price texts
yen_matches = []
for el in soup.find_all(string=re.compile(r'[0-9,]+円|￥|¥')):
    txt = el.strip()
    if txt and len(txt) < 80:
        yen_matches.append(txt)

print("\nPrices found:")
for y in list(dict.fromkeys(yen_matches))[:15]:
    print(" ", y)
