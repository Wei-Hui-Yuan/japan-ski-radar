import sys
sys.stdout.reconfigure(encoding='utf-8')
from curl_cffi import requests

url = "https://travel.rakuten.co.jp/"
r = requests.get(url, impersonate="chrome120")
print("Top status:", r.status_code, "len:", len(r.text))
