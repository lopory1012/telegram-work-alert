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
weekday = now.weekday()  # 월=0, 화=1, 수=2, 목=3, 금=4, 토=5, 일=6
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
    # ── 기존 취합 알림 ──────────────────────────
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

    # ── 기도회 안내 (일/월/수/목/금 22시) ──────────
    elif weekday in (6, 0, 2, 3, 4) and in_window(22, 0) and "pray_reminder" not in sent_today:
        message = "🙏 내일은 오전 7시 기도회가 있는 날입니다. 함께 기도합시다."
        key = "pray_reminder"

    # ── 전도단 실참 누적 (금 10/17/20/22시) ────────
    elif weekday == 4 and in_window(10, 0) and "mission_10" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!"
        key = "mission_10"
    elif weekday == 4 and in_window(17, 0) and "mission_17" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!"
        key = "mission_17"
    elif weekday == 4 and in_window(20, 0) and "mission_20" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!"
        key = "mission_20"
    elif weekday == 4 and in_window(22, 0) and "mission_22" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!"
        key = "mission_22"

    # ── 신앙교육 실참 누적 (화 9:50/17/20/22시) ────
    elif weekday == 1 and in_window(9, 50) and "edu_0950" not in sent_today:
        message = "📋 신앙교육 실참 누적 해주세요!"
        key = "edu_0950"
    elif weekday == 1 and in_window(17, 0) and "edu_17" not in sent_today:
        message = "📋 신앙교육 실참 누적 해주세요!"
        key = "edu_17"
    elif weekday == 1 and in_window(20, 0) and "edu_20" not in sent_today:
        message = "📋 신앙교육 실참 누적 해주세요!"
        key = "edu_20"
    elif weekday == 1 and in_window(22, 0) and "edu_22" not in sent_today:
        message = "📋 신앙교육 실참 누적 해주세요!"
        key = "edu_22"

    # ── 심방보고 마감 안내 (목 10시) ────────────────
    elif weekday == 3 and in_window(10, 0) and "visit_report" not in sent_today:
        message = "📌 오늘은 심방보고 마감날입니다!"
        key = "visit_report"


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
