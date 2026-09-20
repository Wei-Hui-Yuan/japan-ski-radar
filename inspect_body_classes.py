import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://nozawakanko.jp/genre/stay/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

# Find main content container
for div in soup.find_all("div", class_=True):
    clz = " ".join(div.get("class", []))
    if any(k in clz for k in ["list", "post", "stay", "archive", "content"]):
        print(f"Found class: {clz}")

# Print snippet of body
print("Body snippet:")
print(soup.body.get_text(separator="\n", strip=True)[:1000])
