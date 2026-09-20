import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availabilitylist"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily"
}
params = {"planType": "1", "fromDate": "2026-12-29"}
r = requests.get(url, params=params, headers=headers, timeout=15)
data = r.json()

for cid, html in list(data["calendars"].items())[:3]:
    print(f"=== Calendar for {cid} (len: {len(html)}) ===")
    print(html[:1500])
