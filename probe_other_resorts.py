import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

urls = [
    ("Hakuba", "https://www.hakubavalley.com/en/accommodation/"),
    ("Hakuba Village", "https://www.vill.hakuba.nagano.jp/"),
    ("Madarao", "https://www.madarao.jp/hotel/"),
    ("Shiga Kogen", "https://www.shigakogen.gr.jp/hotel/"),
    ("Shiga Kogen 2", "https://shigakogen-ski.or.jp/")
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for name, u in urls:
    try:
        r = requests.get(u, headers=headers, timeout=10)
        print(f"{name} ({u}) -> Status: {r.status_code}, Length: {len(r.text)}")
    except Exception as e:
        print(f"{name} ({u}) -> Error: {e}")
