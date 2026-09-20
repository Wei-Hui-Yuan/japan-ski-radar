import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://nozawakanko.jp/spot/spot-1017/"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

print("Title tag:", soup.title.string if soup.title else "")
# Look for headings or spot name
for h in soup.find_all(["h1", "h2", "h3", "div", "span"], class_=True):
    clz = " ".join(h.get("class", []))
    if any(k in clz for k in ["title", "name", "spot", "heading"]):
        print(f"[{clz}] -> {h.get_text(strip=True)[:100]}")
