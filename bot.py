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

message = None

# GitHub Actions에서 수동으로 "Run workflow" 했을 때 테스트 알림
if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
    message = "🔔 테스트 알림입니다.\n텔레그램 봇이 정상적으로 연결되었습니다."

else:
    # 매일 23:50
    if current_time == "23:50":
        message = "🔔 일일보고 작성 시간입니다."

    # 일요일 21:50
    elif weekday == 6 and current_time == "21:50":
        message = "🔔 신앙관리교육 사전취합 시간입니다."

    # 월요일 21:50
    elif weekday == 0 and current_time == "21:50":
        message = "🔔 수요일 사전예배 사전취합 시간입니다."

    # 목요일 21:50
    elif weekday == 3 and current_time == "21:50":
        message = "🔔 구역예배 취합 시간입니다."

    # 금요일 21:50
    elif weekday == 4 and current_time == "21:50":
        message = "🔔 전도단 사전취합 / 주일예배 사전취합 시간입니다."


# message가 존재할 때만 텔레그램 전송
if message:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request) as response:
        print(response.read().decode())

    print("알림 전송 완료:", message)

else:
    print("조건에 맞는 알림 시간이 아닙니다. 전송을 스킵합니다.")
