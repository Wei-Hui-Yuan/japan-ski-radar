import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

urls = [
    ("Goryukan Hakuba", "https://reserve.489ban.net/hakuba-nagano/goryukan/0/plan"),
    ("Azumaya Nozawa", "https://reserve.489ban.net/nozawakanko/azumaya/0/plan"),
    ("Utopia Nozawa", "https://reserve.489ban.net/nozawakanko/yutopia/0/plan"),
    ("Kiriya Ryokan Nozawa", "https://reserve.489ban.net/nozawakanko/kiriya/0/plan"),
    ("Madarao Hotel", "https://d-reserve.jp/GSEA001F01300/GSEA001A01?hotelCode=0000001749")
]

headers = {"User-Agent": "Mozilla/5.0"}

for name, u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Find any text containing yen symbol or 円
        yen_matches = []
        for el in soup.find_all(["span", "div", "p", "strong", "em"]):
            txt = el.get_text(strip=True)
            if re.search(r'(¥|￥|[0-9,]+円)', txt) and len(txt) < 80:
                yen_matches.append(txt)
                
        print(f"\n=== {name} ===")
        print(f"URL: {u}")
        print(f"Price snippets found ({len(yen_matches)}):")
        unique_matches = list(dict.fromkeys(yen_matches))
        for m in unique_matches[:6]:
            print(f"  {m}")
    except Exception as e:
        print(f"Error {name}: {e}")
