import os
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "948070176"

now = datetime.now(ZoneInfo("Asia/Seoul"))

weekday = now.weekday()
current_time = now.strftime("%H:%M")

messages = {}

# 매일 23:50
if current_time == "23:50":
    messages["23:50"] = "🔔 일일보고 작성 시간입니다."

# 일요일 21:50
if weekday == 6 and current_time == "21:50":
    messages["21:50"] = "🔔 신앙관리교육 사전취합 시간입니다."

# 월요일 21:50
if weekday == 0 and current_time == "21:50":
    messages["21:50"] = "🔔 수요일 사전예배 사전취합 시간입니다."

# 목요일 21:50
if weekday == 3 and current_time == "21:50":
    messages["21:50"] = "🔔 구역예배 취합 시간입니다."

# 금요일 21:50
if weekday == 4 and current_time == "21:50":
    messages["21:50"] = "🔔 전도단 사전취합 / 주일예배 사전취합 시간입니다."


if current_time in messages:
    message = messages[current_time]

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request) as response:
        print(response.read().decode())
else:
    print("현재 시간에는 예정된 알림이 없습니다.")
