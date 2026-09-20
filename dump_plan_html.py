import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

page_url = "https://reserve.489ban.net/nozawakanko/azumaya/0/plan"
r_page = session.get(page_url)
soup_page = BeautifulSoup(r_page.text, "html.parser")
csrf_token = soup_page.select_one("meta[name='csrf-token']").get("content")

r_post = session.post(
    "https://reserve.489ban.net/nozawakanko/azumaya/0/planlist",
    headers={"X-CSRF-TOKEN": csrf_token, "X-Requested-With": "XMLHttpRequest"}
)

html = r_post.json()["planList"]
print(html[:2000])
