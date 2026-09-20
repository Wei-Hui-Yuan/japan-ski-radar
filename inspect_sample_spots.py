import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

urls = [
    "https://nozawakanko.jp/spot/spot-1017/",
    "https://nozawakanko.jp/spot/spot1998/",
    "https://nozawakanko.jp/spot/spot-10446/"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for u in urls:
    r = requests.get(u, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find(["h1", "h2"])
    title_text = title.get_text(strip=True) if title else "No title"
    print(f"\n--- {u} ---")
    print("Title:", title_text)
    
    # Extract details table or DL/DT/DD
    details = {}
    for tr in soup.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if th and td:
            details[th.get_text(strip=True)] = td.get_text(strip=True)
            # check link in td
            a = td.find("a", href=True)
            if a:
                details[th.get_text(strip=True) + "_link"] = a["href"]
    
    for k, v in details.items():
        print(f"  {k}: {v}")
