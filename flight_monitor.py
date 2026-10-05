import os
import requests

webhook = os.environ["DISCORD_WEBHOOK"]

message = """
✈️ 機票監控測試成功！

航線：
桃園 TPE → 釜山 PUS

日期：
2027/02/19 → 2027/02/21

去程：
15:00–19:00

預算：
NT$11,000
"""

response = requests.post(
    webhook,
    json={
        "content": message
    },
    timeout=30
)

response.raise_for_status()

print("Discord 通知成功！")


