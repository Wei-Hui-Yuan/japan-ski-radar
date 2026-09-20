import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

url = "https://reserve.489ban.net/nozawakanko/azumaya/0/plan"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

for s in soup.find_all("script"):
    txt = s.string or ""
    if any(k in txt for k in ["ajax", "url", "plan", "price", "api", "get"]):
        print("--- SCRIPT MATCH ---")
        for line in txt.split("\n"):
            if any(k in line for k in ["url", "http", "api", "plan", "price"]):
                print(" ", line.strip())
