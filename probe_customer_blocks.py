import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

# Let's see how each customer block is rendered in the HTML
print("Finding all customer elements...")
for card in soup.select("[data-customer-id]"):
    cid = card.get("data-customer-id")
    # print surrounding tags
    parent = card.parent
    grand = parent.parent if parent else None
    print(f"\nCID: {cid}")
    print("Parent classes/tag:", parent.name, parent.get("class"))
    if grand:
        print("Grandparent text snippet:", grand.get_text(strip=True)[:100])
