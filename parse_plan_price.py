import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
from dump_plan_html import html

soup = BeautifulSoup(html, "html.parser")
for sec in soup.select("section.plan-list"):
    h2 = sec.select_one("h2")
    title = h2.get_text(strip=True) if h2 else "No title"
    text = sec.get_text(separator="\n", strip=True)
    print("Plan:", title)
    for line in text.split("\n"):
        if any(k in line for k in ["円", "￥", "¥", "料金", "名", "泊"]):
            print("  ", line)
