import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://www.hakubavalley.com/en/accommodation/"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    href = a["href"]
    if any(k in href for k in ["booking", "hotel", "stay", "reserve", "resort", "lodge", "pension"]):
        print(f"  {txt} -> {href}")
