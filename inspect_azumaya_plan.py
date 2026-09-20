import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/nozawakanko/azumaya/0/plan"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")
print(soup.get_text(separator="\n", strip=True)[:1500])
