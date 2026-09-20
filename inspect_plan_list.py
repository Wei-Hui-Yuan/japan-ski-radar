import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

plans = soup.select(".c-plan-card, .plan-card, [class*='plan']")
print("Total elements with 'plan' in class:", len(plans))

# Find all links to clients or plans
links = soup.find_all("a", href=True)
client_links = set()
for a in links:
    h = a["href"]
    t = a.get_text(strip=True)
    if "/client/" in h:
        client_links.add((t, h))

print(f"\nUnique /client/ links found ({len(client_links)}):")
for t, h in list(client_links)[:25]:
    print(f"  {t} -> {h}")
