import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

page_url = "https://reserve.489ban.net/nozawakanko/azumaya/0/plan"
r_page = session.get(page_url)
soup_page = BeautifulSoup(r_page.text, "html.parser")
csrf_token = soup_page.select_one("meta[name='csrf-token']").get("content")

r_post = session.post(
    "https://reserve.489ban.net/nozawakanko/azumaya/0/planlist",
    headers={"X-CSRF-TOKEN": csrf_token, "X-Requested-With": "XMLHttpRequest"}
)

soup = BeautifulSoup(r_post.json()["planList"], "html.parser")
for art in soup.find_all(["article", "div"], class_=re.compile(r"plan|card", re.I)):
    title = art.find(["h2", "h3", "h4", "p"], class_=re.compile(r"title|name", re.I))
    if title:
        t = title.get_text(strip=True)
        # Find all prices within this article
        prices = [p.get_text(strip=True) for p in art.find_all(class_=re.compile(r"price|amount|yen", re.I))]
        all_yen = [el.strip() for el in art.find_all(string=re.compile(r'[0-9,]+円|￥|¥')) if el.strip()]
        print(f"Title: {t}")
        print(f"  Prices: {prices}")
        print(f"  All Yen strings: {all_yen}")
