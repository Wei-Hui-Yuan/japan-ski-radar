import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

for s in soup.find_all("script"):
    txt = s.string or ""
    if "baseDate" in txt or "ajax" in txt or "fetch" in txt or "client" in txt:
        print("=== SCRIPT ===")
        print(txt)
