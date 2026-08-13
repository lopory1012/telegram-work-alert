import os
import json
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "948070176"
LOG_FILE = "sent_log.json"
TOLERANCE = 3  # 5분마다 도니까 오차범위는 좁게

now = datetime.now(ZoneInfo("Asia/Seoul"))
weekday = now.weekday()
now_total = now.hour * 60 + now.minute
today_str = now.strftime("%Y-%m-%d")

def in_window(h, m):
    return abs(now_total - (h * 60 + m)) <= TOLERANCE

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)
else:
    log = {}

sent_today = log.get(today_str, [])

message = None
key = None

if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
    message = "🔔 테스트 알림입니다.\n텔레그램 봇이 정상적으로 연결되었습니다."
else:
    if in_window(23, 50) and "daily" not in sent_today:
        message = "🔔 일일보고 작성 시간입니다."
        key = "daily"
    elif weekday == 6 and in_window(21, 50) and "sun" not in sent_today:
        message = "🔔 신앙관리교육 사전취합 시간입니다."
        key = "sun"
    elif weekday == 0 and in_window(21, 50) and "mon" not in sent_today:
        message = "🔔 수요일 사전예배 사전취합 시간입니다."
        key = "mon"
    elif weekday == 3 and in_window(21, 50) and "thu" not in sent_today:
        message = "🔔 구역예배 취합 시간입니다."
        key = "thu"
    elif weekday == 4 and in_window(21, 50) and "fri" not in sent_today:
        message = "🔔 전도단 사전취합 / 주일예배 사전취합 시간입니다."
        key = "fri"

if message:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": message}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
    print("알림 전송 완료:", message)

    if key:
        log.setdefault(today_str, []).append(key)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
else:
    print("현재 알림 시간이 아니거나 이미 전송됨.")
