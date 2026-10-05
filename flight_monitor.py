import os
import requests

API_KEY = os.environ["IGNAV_API_KEY"]
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

url = "https://ignav.com/api/fares/round-trip"

payload = {
    "origin": "TPE",
    "destination": "PUS",
    "departure_date": "2027-02-19",
    "return_date": "2027-02-21",
    "adults": 1,
    "cabin_class": "economy",
    "market": "TW",
    "departure_time_range": {
        "earliest_hour": 15,
        "latest_hour": 19
    }
}

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

print("開始查詢機票...")

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=90
)

print("HTTP:", response.status_code)

response.raise_for_status()

data = response.json()

itineraries = data.get("itineraries", [])
print("\n===== 行程資料檢查 =====")

for i, itinerary in enumerate(itineraries[:3], 1):
    print(f"\n--- 行程 {i} ---")

    print("價格：")
    print(itinerary.get("price"))

    print("行李：")
    print(itinerary.get("baggage"))

    print("去程：")
    print(itinerary.get("outbound"))

    print("回程：")
    print(itinerary.get("inbound"))

    print("連結：")
    print(itinerary.get("url"))

print("\n===== 檢查結束 =====")


print("找到航班數量:", len(itineraries))

if not itineraries:
    message = """
⚠️ **Ignav 查價結果**

目前沒有找到符合條件的來回航班。

✈️ TPE → PUS
📅 2027/02/19 → 2027/02/21
🕒 去程 15:00–19:00
💺 經濟艙
👤 1 位成人
"""

else:

    # 按總價由低到高
    itineraries.sort(
        key=lambda x: x.get("price", {}).get("amount", 999999999)
    )

    cheapest = itineraries[0]

    price = cheapest.get("price", {})
    amount = price.get("amount")
    currency = price.get("currency", "TWD")

    outbound = cheapest.get("outbound", {})
    inbound = cheapest.get("inbound", {})

    outbound_segments = outbound.get("segments", [])
    inbound_segments = inbound.get("segments", [])

    outbound_first = (
        outbound_segments[0]
        if outbound_segments
        else {}
    )

    outbound_last = (
        outbound_segments[-1]
        if outbound_segments
        else {}
    )

    inbound_first = (
        inbound_segments[0]
        if inbound_segments
        else {}
    )

    inbound_last = (
        inbound_segments[-1]
        if inbound_segments
        else {}
    )

    airline = outbound.get(
        "carrier",
        "未知航空公司"
    )

    departure_time = outbound_first.get(
        "departure_time_local",
        "未知"
    )

    arrival_time = outbound_last.get(
        "arrival_time_local",
        "未知"
    )

    return_departure = inbound_first.get(
        "departure_time_local",
        "未知"
    )

    return_arrival = inbound_last.get(
        "arrival_time_local",
        "未知"
    )

    message = f"""
✈️ **機票查價成功！**

🛫 桃園 TPE → 釜山 PUS

📅 去程：2027/02/19
🕒 去程：{departure_time}

📅 回程：2027/02/21
🕒 回程：{return_departure}

🏷️ 航空公司：
{airline}

💰 **最低價格：{currency} {amount:,}**

🛬 去程抵達：
{arrival_time}

🛬 回程抵達：
{return_arrival}

🔎 找到 {len(itineraries)} 個行程
"""

requests.post(
    DISCORD_WEBHOOK,
    json={
        "content": message
    },
    timeout=30
).raise_for_status()

print("Discord 通知成功")
