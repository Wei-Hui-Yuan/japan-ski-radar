import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/search?unspecifiedDate=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

# Check main content div or error/notice message
main = soup.select_one("main, #main, .main-contents, .l-main, body")
print("Text snippet of page:")
if main:
    print(main.get_text(separator="\n", strip=True)[:1500])

# Check scripts to see if Vue/React or XHR endpoints are used
scripts = [s.get("src") for s in soup.find_all("script") if s.get("src")]
print("\nScripts found:", scripts)
