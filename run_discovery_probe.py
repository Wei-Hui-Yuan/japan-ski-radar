import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import json
import csv
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

results = []

print("=== 1. Probing Nozawa Onsen (489ban Tourism Bureau Group) ===")
try:
    # 1. Get daily calendar page to extract lodge metadata
    daily_url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availability/daily"
    r_page = requests.get(daily_url, headers={"User-Agent": headers["User-Agent"]}, timeout=15)
    soup_page = BeautifulSoup(r_page.text, "html.parser")
    
    # 2. Get availability API data
    api_url = "https://reserve.489ban.net/group/client/nozawakanko/0/plan/availabilitylist"
    r_api = requests.get(api_url, params={"planType": "1", "fromDate": "2026-12-29"}, headers=headers, timeout=15)
    api_data = r_api.json()
    calendars = api_data.get("calendars", {})
    
    # Parse each lodge block
    for div in soup_page.select(".customer-calendars"):
        cid = div.get("data-customer-id")
        summary = div.find_parent("div", class_="webc_summary") or div.parent
        card = summary.parent if summary else div.parent
        
        name = "Unknown Lodge"
        address = ""
        phone = ""
        description = ""
        
        if card:
            title_el = card.find(["h2", "h3", "h4", "p", "strong"], class_=re.compile(r"title|name|heading|tit", re.I))
            full_text = card.get_text(" ", strip=True)
            
            # Match phone
            m_phone = re.search(r'(0\d{1,4}-\d{1,4}-\d{3,4})', full_text)
            if m_phone:
                phone = m_phone.group(1)
            
            # Match address
            m_addr = re.search(r'長野県[^\s電話]+', full_text)
            if m_addr:
                address = m_addr.group(0)
                
            # Extract name
            lines = [l.strip() for l in full_text.split(" ") if l.strip()]
            if lines:
                name = lines[0]
                if "住所" in name:
                    name = name.split("住所")[0]
        
        # Check availability in calendar
        cal_html = calendars.get(cid, "")
        cal_soup = BeautifulSoup(cal_html, "html.parser")
        
        # Check Dec 29, 30, 31, Jan 1 availability links
        avail_links = [a["href"] for a in cal_soup.find_all("a", href=True)]
        
        # Determine status
        status = "Not Opened / Fully Booked"
        direct_url = f"https://reserve.489ban.net/group/client/nozawakanko/0/plan"
        if avail_links:
            status = f"Available ({len(avail_links)} dates in range)"
            direct_url = avail_links[0]
            
        results.append({
            "resort": "Nozawa Onsen",
            "name": name,
            "cid": cid,
            "booking_engine": "489ban Group (Nozawa Tourism Bureau)",
            "status": status,
            "available_dates_found": len(avail_links),
            "phone": phone,
            "address": address,
            "direct_link": direct_url,
            "notes": "Traditional onsen ryokan/pension; New Year reservations may open on staggered schedule (check direct/phone)"
        })
    print(f"Captured {len(soup_page.select('.customer-calendars'))} Nozawa Onsen lodges.")
except Exception as e:
    print(f"Error probing Nozawa: {e}")

print("\n=== 2. Probing Hakuba Village (489ban Tourism Bureau Group) ===")
try:
    daily_url = "https://reserve.489ban.net/group/client/hakuba-nagano/0/plan/availability/daily"
    r_page = requests.get(daily_url, headers={"User-Agent": headers["User-Agent"]}, timeout=15)
    soup_page = BeautifulSoup(r_page.text, "html.parser")
    
    api_url = "https://reserve.489ban.net/group/client/hakuba-nagano/0/plan/availabilitylist"
    r_api = requests.get(api_url, params={"planType": "1", "fromDate": "2026-12-29"}, headers=headers, timeout=15)
    api_data = r_api.json()
    calendars = api_data.get("calendars", {})
    
    for div in soup_page.select(".customer-calendars"):
        cid = div.get("data-customer-id")
        parent = div.parent
        grand = parent.parent if parent else None
        
        name = "Unknown Hakuba Lodge"
        if grand:
            title = grand.find(["h2", "h3", "h4", "p", "a"])
            if title:
                name = title.get_text(strip=True)
                if "住所" in name:
                    name = name.split("住所")[0]
        
        cal_html = calendars.get(cid, "")
        cal_soup = BeautifulSoup(cal_html, "html.parser")
        avail_links = [a["href"] for a in cal_soup.find_all("a", href=True)]
        
        status = "Not Opened / Fully Booked"
        direct_url = f"https://reserve.489ban.net/group/client/hakuba-nagano/0/plan"
        notes = "Hakuba lodge"
        if avail_links:
            status = f"Available ({len(avail_links)} dates in window)"
            direct_url = avail_links[0]
            if cid == "1847": # Goryukan
                notes = "Min 5 nights until Oct 1 (3-night opens Oct 1; 1-night opens Nov 1)"
                
        results.append({
            "resort": "Hakuba Valley",
            "name": name,
            "cid": cid,
            "booking_engine": "489ban Group (Hakuba Tourism)",
            "status": status,
            "available_dates_found": len(avail_links),
            "phone": "",
            "address": "白馬村, 長野県",
            "direct_link": direct_url,
            "notes": notes
        })
    print(f"Captured {len(soup_page.select('.customer-calendars'))} Hakuba lodges.")
except Exception as e:
    print(f"Error probing Hakuba: {e}")

print("\n=== 3. Adding Key Direct & Regional Lodges ===")
# Add Madarao & other key Nagano spots
results.append({
    "resort": "Madarao Kogen",
    "name": "Madarao Kogen Hotel",
    "cid": "0000001749",
    "booking_engine": "DirectIn (Dynatech)",
    "status": "Check Live Calendar",
    "available_dates_found": 0,
    "phone": "0269-64-3311",
    "address": "長野県飯山市斑尾高原",
    "direct_link": "https://d-reserve.jp/GSEA001F01300/GSEA001A01?hotelCode=0000001749",
    "notes": "Direct ski-in/ski-out hotel with natural hot spring; 25 mins bus from Iiyama Shinkansen"
})

results.append({
    "resort": "Nozawa Onsen",
    "name": "Nozawa Onsen Tourism Bureau Direct Inquiry Clearing",
    "cid": "TOURISM_FORM",
    "booking_engine": "Official Tourism Concierge Matching",
    "status": "Direct Request Available",
    "available_dates_found": 1,
    "phone": "0269-85-3155",
    "address": "長野県下高井郡野沢温泉村大字豊郷5043-3",
    "direct_link": "https://docs.google.com/forms/d/e/1FAIpQLSdV7vpETa9Yu9dwJB-92oyWYr7ibMgYvO5ZIThRy5PzGfecGg/viewform?usp=sharing&ouid=112515000462406041687",
    "notes": "Tourism association manual matching service for unlisted ryokan/minshuku rooms"
})

# Write to CSV
csv_filename = "lodges_discovery_probe.csv"
fieldnames = ["resort", "name", "cid", "booking_engine", "status", "available_dates_found", "phone", "address", "direct_link", "notes"]

with open(csv_filename, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\n[SUCCESS] Wrote {len(results)} lodges to {csv_filename}")
