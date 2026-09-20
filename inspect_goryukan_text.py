import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/hakuba-nagano/goryukan/0/plan/search?date=2026-12-29&numberOfNights=1&roomCount=1&adult=2"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

# Print text snippet
text = soup.get_text(separator="\n", strip=True)
lines = [l for l in text.split("\n") if l.strip()]
print("Page snippet:")
for l in lines[:30]:
    print(" ", l)
