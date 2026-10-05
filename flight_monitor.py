import os
import requests
from bs4 import BeautifulSoup

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

URL = (
    "https://www.google.com/travel/flights"
    "?hl=zh-TW"
    "&curr=TWD"
    "&f=0"
    "&tfs="
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

print("HTTP:", response.status_code)
print("網頁大小:", len(response.text))

if response.status_code != 200:
    raise Exception(
        f"Google Flights 無法取得，HTTP {response.status_code}"
    )

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

text = soup.get_text(" ", strip=True)

print(text[:3000])

message = """
🧪 Google Flights 免費查價測試

GitHub 已成功連線 Google Flights。

接下來會測試：
✈️ TPE → PUS
📅 2027/02/19 → 2027/02/21
🕒 去程 15:00–19:00
💰 預算 NT$11,000

請查看 GitHub Actions 執行結果。
"""

requests.post(
    WEBHOOK,
    json={"content": message},
    timeout=30
).raise_for_status()

print("Discord 測試通知成功")
