import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. Inspect Hakuba Valley
r_hakuba = requests.get("https://www.hakubavalley.com/en/accommodation/", headers=headers, timeout=12)
soup_h = BeautifulSoup(r_hakuba.text, "html.parser")
print("=== HAKUBA VALLEY ACCOMMODATIONS ===")
h_cards = soup_h.select(".c-card, .card, .item, article, [class*='post'], a[href*='accommodation/']")
print("Hakuba items:", len(h_cards))
# Look for lodge links
hakuba_lodges = []
for a in soup_h.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if "accommodation/" in href and text and len(text) > 3 and "accommodation/" != href:
        hakuba_lodges.append((text, href))
for t, h in hakuba_lodges[:10]:
    print(f"  {t} -> {h}")

# 2. Inspect Madarao
r_madarao = requests.get("https://www.madarao.jp/hotel/", headers=headers, timeout=12)
soup_m = BeautifulSoup(r_madarao.text, "html.parser")
print("\n=== MADARAO ACCOMMODATIONS ===")
m_links = []
for a in soup_m.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if any(k in href for k in ["hotel", "pension", "stay"]) and text and len(text) > 2:
        m_links.append((text, href))
for t, h in m_links[:10]:
    print(f"  {t} -> {h}")
