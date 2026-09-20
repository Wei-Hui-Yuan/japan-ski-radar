import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://travel.rakuten.co.jp/"
r = requests.get(url, impersonate="chrome120")
soup = BeautifulSoup(r.text, "html.parser")

for f in soup.find_all("form"):
    act = f.get("action", "")
    if "searchVacant" in act:
        print("Action:", act)
        for i in f.find_all(["input", "select"]):
            print(f"  {i.get('name')} = {i.get('value')} (type: {i.get('type')})")
