import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://www.vill.hakuba.nagano.jp/"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers, timeout=12)
soup = BeautifulSoup(r.text, "html.parser")

print("Hakuba Tourism Title:", soup.title.string if soup.title else "")
# Look for search forms or accommodation links
for a in soup.find_all("a", href=True):
    h = a["href"]
    t = a.get_text(strip=True)
    if any(k in h for k in ["stay", "hotel", "yoyaku", "reserve", "489", "tripla", "booking"]):
        print(f"  {t} -> {h}")

for f in soup.find_all("form"):
    print("Hakuba form action:", f.get("action"))
