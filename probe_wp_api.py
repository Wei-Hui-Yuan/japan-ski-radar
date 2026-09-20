import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

# Let's check WordPress categories or pagination on nozawakanko.jp
# E.g. /genre/stay/page/2/, /spot-cat/..., /stay-cat/...
urls_to_test = [
    "https://nozawakanko.jp/genre/stay/",
    "https://nozawakanko.jp/genre/stay/page/2/",
    "https://nozawakanko.jp/spot/?genre=stay",
    "https://nozawakanko.jp/spot-genre/stay/",
    "https://nozawakanko.jp/spot-tag/stay/",
    "https://nozawakanko.jp/stay-hotel/",
    "https://nozawakanko.jp/stay-minshuku/",
    "https://nozawakanko.jp/wp-json/wp/v2/posts?categories=stay",
    "https://nozawakanko.jp/wp-json/wp/v2/categories",
    "https://nozawakanko.jp/wp-json/wp/v2/types"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for u in urls_to_test:
    try:
        r = requests.get(u, headers=headers, timeout=8)
        print(f"{u} -> status {r.status_code}, len: {len(r.text)}")
    except Exception as e:
        print(f"{u} -> error: {e}")
