import os
import json
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "948070176"
LOG_FILE = "sent_log.json"
TOLERANCE = 3

MISSION_CHAT_ID = "-1001940900666"
EDU_CHAT_ID = "-1003809710264"

now = datetime.now(ZoneInfo("Asia/Seoul"))
weekday = now.weekday()
now_total = now.hour * 60 + now.minute
today_str = now.strftime("%Y-%m-%d")


def in_window(h, m):
    return abs(now_total - (h * 60 + m)) <= TOLERANCE


def api_call(method, payload):
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/" + method
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def send_message(chat_id, text):
    result = api_call("sendMessage", {"chat_id": chat_id, "text": text})
    print("메시지 전송:", result.get("ok"))
    return result


def send_poll(chat_id, question):
    result = api_call("sendPoll", {
        "chat_id": chat_id,
        "question": question,
        "options": json.dumps(["참석"], ensure_ascii=False),
        "is_anonymous": "false"
    })
    print("투표 생성:", result.get("ok"))
    return result


if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)
else:
    log = {}

sent_today = log.get(today_str, {})
if isinstance(sent_today, list):
    sent_today = {k: True for k in sent_today}

message = None
key = None

poll_room_chat_id = None
poll_question = None


if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
    message = "테스트 알림입니다. 텔레그램 봇이 정상적으로 연결되었습니다."

else:
    if in_window(23, 50) and "daily" not in sent_today:
        message = "일일보고 작성 시간입니다.\nhttps://t.me/c/3879535253/14"
        key = "daily"
    elif weekday == 6 and in_window(21, 50) and "sun" not in sent_today:
        message = "신앙관리교육 사전취합 시간입니다.\nhttps://t.me/c/3809710264/3"
        key = "sun"
    elif weekday == 0 and in_window(21, 50) and "mon" not in sent_today:
        message = "수요일 사전예배 사전취합 시간입니다.\nhttps://t.me/c/2817611748/5580"
        key = "mon"
    elif weekday == 3 and in_window(21, 50) and "thu" not in sent_today:
        message = "구역예배 취합 시간입니다.\nhttps://t.me/abcde0156"
        key = "thu"
    elif weekday == 4 and in_window(21, 50) and "fri" not in sent_today:
        message = (
            "전도단 사전취합 / 주일예배 사전취합 시간입니다.\n"
            "전도단: https://t.me/c/1940900666/11868\n"
            "주일예배: https://t.me/c/2817611748/5580"
        )
        key = "fri"

    elif weekday in (6, 0, 2, 3, 4) and in_window(22, 0) and "pray_reminder" not in sent_today:
        message = "내일은 오전 7시 기도회가 있는 날입니다. 함께 기도합시다.\nhttps://t.me/suwon_gather_bot"
        key = "pray_reminder"

    # ── 전도단 실참 체크 (금 10/17/20/22시, 시간대별 개별 투표) ──
    elif weekday == 4 and in_window(10, 0) and "mission_10" not in sent_today:
        key = "mission_10"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 10:00 실참 체크"
    elif weekday == 4 and in_window(17, 0) and "mission_17" not in sent_today:
        key = "mission_17"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 17:00 실참 체크"
    elif weekday == 4 and in_window(20, 0) and "mission_20" not in sent_today:
        key = "mission_20"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 20:00 실참 체크"
    elif weekday == 4 and in_window(22, 0) and "mission_22" not in sent_today:
        key = "mission_22"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 22:00 실참 체크"

    # ── 신앙교육 실참 체크 (화 9:50/17/20/22시, 시간대별 개별 투표) ──
    elif weekday == 1
