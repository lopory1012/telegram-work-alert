import os
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "948070176"

now = datetime.now(ZoneInfo("Asia/Seoul"))

# 월~금만 알림
if now.weekday() < 5:

    messages = {
        "10:00": "🔔 지금은 취합할 시간입니다.",
        "14:00": "🔔 지금은 취합할 시간입니다.",
        "17:00": "🔔 오늘 취합 업무를 마무리할 시간입니다."
    }

    current_time = now.strftime("%H:%M")

    if current_time in messages:
        message = messages[current_time]

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        data = urllib.parse.urlencode({
            "chat_id": CHAT_ID,
            "text": message
        }).encode()

        urllib.request.urlopen(
            urllib.request.Request(url, data=data)
        )

        print("알림 전송:", message)
    else:
        print("현재 알림 시간이 아닙니다.")
else:
    print("주말이므로 알림을 보내지 않습니다.")
