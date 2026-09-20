import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup

url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availabilitylist"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily"
}
params = {"planType": "1", "fromDate": "2026-12-29"}
r = requests.get(url, params=params, headers=headers, timeout=15)
data = r.json()

# Also get lodge names from the daily page
page_r = requests.get("https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily", headers=headers, timeout=15)
soup = BeautifulSoup(page_r.text, "html.parser")

# Let's find customer names properly
customer_cards = soup.select(".client_item, [class*='client'], .customer-calendars")
# Print all text in the calendar wrapper
for div in soup.select(".customer-calendars"):
    cid = div.get("data-customer-id")
    # find preceding heading
    h = div.find_previous(["h2", "h3", "h4", "p", "a"])
    h_text = h.get_text(strip=True) if h else "Unknown"
    
    cal_html = data["calendars"].get(cid, "")
    cal_soup = BeautifulSoup(cal_html, "html.parser")
    rows = cal_soup.select("tbody tr")
    print(f"\n--- Customer ID {cid} : Preceding text: {h_text} ---")
    for r_idx, row in enumerate(rows):
        cells = [td.get_text(strip=True) or (td.find("a").get("href") if td.find("a") else "-") for td in row.find_all("td")]
        classes = [td.get("class", []) for td in row.find_all("td")]
        print(f"  Row {r_idx}: {cells}")
        print(f"  Classes: {classes}")
