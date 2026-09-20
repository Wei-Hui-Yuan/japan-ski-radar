import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://travel.rakuten.co.jp/"
r = requests.get(url, impersonate="chrome120")
soup = BeautifulSoup(r.text, "html.parser")

for f in soup.find_all("form"):
    if "searchVacant" in f.get("action", ""):
        for i in f.find_all("input"):
            if i.get("type") in ["text", "hidden"] and i.get("id"):
                print(f"id={i.get('id')}, name={i.get('name')}, placeholder={i.get('placeholder')}, val={i.get('value')}")
