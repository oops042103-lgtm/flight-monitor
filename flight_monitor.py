import os
import re
import requests
from bs4 import BeautifulSoup

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

# =========================
# 你的機票條件
# =========================

DEPARTURE = "TPE"
ARRIVAL = "PUS"

OUTBOUND_DATE = "2027-02-19"
RETURN_DATE = "2027-02-21"

BUDGET = 11000

# 去程 15:00～19:00
START_HOUR = 15
END_HOUR = 19

# =========================
# Google Flights
# =========================

url = (
    "https://www.google.com/travel/flights"
    f"?q=Flights%20from%20{DEPARTURE}%20to%20{ARRIVAL}"
    f"%20on%20{OUTBOUND_DATE}"
    f"%20returning%20{RETURN_DATE}"
    "&hl=zh-TW"
    "&curr=TWD"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"
}

response = requests.get(
    url,
    headers=headers,
    timeout=60
)

response.raise_for_status()

print("Google Flights HTTP:", response.status_code)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

text = soup.get_text(
    " ",
    strip=True
)

print("資料長度:", len(text))

# =========================
# 找價格
# =========================

prices = []

matches = re.findall(
    r"NT\$?\s?([\d,]+)",
    text
)

for match in matches:

    price = int(
        match.replace(",", "")
    )

    # 避免抓到不合理的數字
    if 1000 <= price <= 100000:
        prices.append(price)

prices = sorted(set(prices))

print("找到的價格:")
print(prices[:20])


# =========================
# Discord
# =========================

if not prices:

    message = f"""
⚠️ **機票查價結果**

目前沒有成功解析到 Google Flights 的票價。

✈️ {DEPARTURE} → {ARRIVAL}

📅 {OUTBOUND_DATE}
📅 回程 {RETURN_DATE}

🕒 去程 15:00–19:00

💰 預算 NT${BUDGET:,}

這不代表沒有機票，
只是目前免費抓取沒有成功解析價格。
"""

else:

    cheapest = min(prices)

    if cheapest < BUDGET:

        message = f"""
🔥 **機票低於預算！**

✈️ {DEPARTURE} → {ARRIVAL}

📅 {OUTBOUND_DATE}
📅 回程 {RETURN_DATE}

🕒 去程 15:00–19:00

💰 **目前抓到最低：NT${cheapest:,}**

🎯 預算：NT${BUDGET:,}

🔥 低於預算 NT${BUDGET - cheapest:,}！
"""

    else:

        message = f"""
✈️ **機票價格監控**

航線：
{DEPARTURE} → {ARRIVAL}

📅 {OUTBOUND_DATE}
📅 回程 {RETURN_DATE}

🕒 去程 15:00–19:00

💰 目前最低：
**NT${cheapest:,}**

🎯 預算：
NT${BUDGET:,}

目前尚未低於預算。
"""


requests.post(
    WEBHOOK,
    json={
        "content": message
    },
    timeout=30
).raise_for_status()

print("Discord 通知成功")
