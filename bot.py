import os
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "948070176"

now = datetime.now(ZoneInfo("Asia/Seoul"))
weekday = now.weekday()  # 월=0 ... 일=6
now_total = now.hour * 60 + now.minute

# 스케줄이 몇 분 늦게 돌아도 알림이 나가도록 허용 범위(분)
TOLERANCE = 20

def in_window(target_hour, target_minute):
    target_total = target_hour * 60 + target_minute
    return abs(now_total - target_total) <= TOLERANCE

message = None

# GitHub Actions에서 수동으로 "Run workflow" 했을 때 테스트 알림
if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
    message = "🔔 테스트 알림입니다.\n텔레그램 봇이 정상적으로 연결되었습니다."

else:
    # 임시 테스트용 - 확인 후 삭제할 것
    if in_window(11, 10):
        message = "🔔 3분 테스트 알림입니다!"
    
    # 매일 23:50
    if in_window(23, 50):
        message = "🔔 일일보고 작성 시간입니다."

    # 일요일 21:50
    elif weekday == 6 and in_window(21, 50):
        message = "🔔 신앙관리교육 사전취합 시간입니다."

    # 월요일 21:50
    elif weekday == 0 and in_window(21, 50):
        message = "🔔 수요일 사전예배 사전취합 시간입니다."

    # 목요일 21:50
    elif weekday == 3 and in_window(21, 50):
        message = "🔔 구역예배 취합 시간입니다."

    # 금요일 21:50
    elif weekday == 4 and in_window(21, 50):
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
    print("현재 알림 시간이 아닙니다.")
