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

MISSION_CHAT_ID = "-5109559157"
EDU_CHAT_ID = "-5109559157"

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


def get_updates(offset):
    result = api_call("getUpdates", {"offset": offset, "timeout": 0})
    return result.get("result", [])


if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)
else:
    log = {}

if "last_update_id" not in log:
    log["last_update_id"] = 0
if "polls" not in log:
    log["polls"] = {}

sent_today = log.get(today_str, {})
if isinstance(sent_today, list):
    sent_today = {k: True for k in sent_today}

# ── 1) 새로 들어온 투표 응답을 먼저 수집해서 누적 저장 ─────────
updates = get_updates(log["last_update_id"] + 1)
for upd in updates:
    log["last_update_id"] = max(log["last_update_id"], upd["update_id"])
    pa = upd.get("poll_answer")
    if not pa:
        continue
    poll_id = pa["poll_id"]
    if poll_id not in log["polls"]:
        continue
    user = pa["user"]
    name = user.get("first_name", "") + (
        (" " + user["last_name"]) if user.get("last_name") else ""
    )
    voters = log["polls"][poll_id].setdefault("voters", {})
    if pa.get("option_ids"):
        voters[str(user["id"])] = name
    else:
        voters.pop(str(user["id"]), None)

with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

# ── 2) 알림/투표 로직 ─────────────────────────
message = None
key = None

poll_room_chat_id = None
poll_question = None
poll_key = None

summary_key = None
summary_for = None
summary_label = None


is_auto_trigger = os.environ.get("INPUT_AUTO") == "true"

if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch" and not is_auto_trigger:

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

    # ── 전도단 실참 체크 투표 생성 (금 10/17/20/22시) ──
    elif weekday == 4 and in_window(10, 0) and "mission_10" not in sent_today:
        key = "mission_10"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 10:00 실참 체크"
        poll_key = "mission_10"
    elif weekday == 4 and in_window(17, 0) and "mission_17" not in sent_today:
        key = "mission_17"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 17:00 실참 체크"
        poll_key = "mission_17"
    elif weekday == 4 and in_window(20, 0) and "mission_20" not in sent_today:
        key = "mission_20"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 20:00 실참 체크"
        poll_key = "mission_20"
    elif weekday == 4 and in_window(22, 0) and "mission_22" not in sent_today:
        key = "mission_22"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 22:00 실참 체크"
        poll_key = "mission_22"

    # ── 신앙교육 실참 체크 투표 생성 (화 9:50/17/20/22시) ──
    elif weekday == 1 and in_window(9, 50) and "edu_0950" not in sent_today:
        key = "edu_0950"
        poll_room_chat_id = EDU_CHAT_ID
        poll_question = "[신앙교육] 09:50 실참 체크"
        poll_key = "edu_0950"
    elif weekday == 1 and in_window(17, 0) and "edu_17" not in sent_today:
        key = "edu_17"
        poll_room_chat_id = EDU_CHAT_ID
        poll_question = "[신앙교육] 17:00 실참 체크"
        poll_key = "edu_17"
    elif weekday == 1 and in_window(20, 0) and "edu_20" not in sent_today:
        key = "edu_20"
        poll_room_chat_id = EDU_CHAT_ID
        poll_question = "[신앙교육] 20:00 실참 체크"
        poll_key = "edu_20"
    elif weekday == 1 and in_window(22, 0) and "edu_22" not in sent_today:
        key = "edu_22"
        poll_room_chat_id = EDU_CHAT_ID
        poll_question = "[신앙교육] 22:00 실참 체크"
        poll_key = "edu_22"

    elif weekday == 3 and in_window(10, 0) and "visit_report" not in sent_today:
        message = "오늘은 심방보고 마감날입니다!\nhttps://t.me/suwon_internal_affair_bot"
        key = "visit_report"

    # ── 명단 요약 (각 취합 시각 + 10분 뒤) ──
    elif weekday == 4 and in_window(10, 10) and "mission_10_summary" not in sent_today:
        summary_key = "mission_10_summary"
        summary_for = "mission_10"
        summary_label = "[전도단] 10:00"
    elif weekday == 4 and in_window(17, 10) and "mission_17_summary" not in sent_today:
        summary_key = "mission_17_summary"
        summary_for = "mission_17"
        summary_label = "[전도단] 17:00"
    elif weekday == 4 and in_window(20, 10) and "mission_20_summary" not in sent_today:
        summary_key = "mission_20_summary"
        summary_for = "mission_20"
        summary_label = "[전도단] 20:00"
    elif weekday == 4 and in_window(22, 10) and "mission_22_summary" not in sent_today:
        summary_key = "mission_22_summary"
        summary_for = "mission_22"
        summary_label = "[전도단] 22:00"
    elif weekday == 1 and in_window(10, 0) and "edu_0950_summary" not in sent_today:
        summary_key = "edu_0950_summary"
        summary_for = "edu_0950"
        summary_label = "[신앙교육] 09:50"
    elif weekday == 1 and in_window(17, 10) and "edu_17_summary" not in sent_today:
        summary_key = "edu_17_summary"
        summary_for = "edu_17"
        summary_label = "[신앙교육] 17:00"
    elif weekday == 1 and in_window(20, 10) and "edu_20_summary" not in sent_today:
        summary_key = "edu_20_summary"
        summary_for = "edu_20"
        summary_label = "[신앙교육] 20:00"
    elif weekday == 1 and in_window(22, 10) and "edu_22_summary" not in sent_today:
        summary_key = "edu_22_summary"
        summary_for = "edu_22"
        summary_label = "[신앙교육] 22:00"


did_something = False

if message:
    send_message(CHAT_ID, message)
    print("알림 전송 완료:", message)
    did_something = True

if poll_room_chat_id and poll_question:
    poll_result = send_poll(poll_room_chat_id, poll_question)
    if poll_result.get("ok"):
        poll_id = poll_result["result"]["poll"]["id"]
        log["polls"][poll_id] = {"key": poll_key, "voters": {}}
        sent_today[poll_key + "_poll_id"] = poll_id
    did_something = True

if summary_key:
    poll_id = sent_today.get(summary_for + "_poll_id")
    names = []
    if poll_id and poll_id in log["polls"]:
        names = list(log["polls"][poll_id].get("voters", {}).values())
    if names:
        text = summary_label + " 실참 명단 (" + str(len(names)) + "명)\n" + ", ".join(names)
    else:
        text = summary_label + " 실참 명단: 아직 없음"
    send_message(CHAT_ID, text)
    print("명단 요약 전송:", text)
    sent_today[summary_key] = True
    did_something = True

if did_something:
    if key:
        sent_today[key] = True
    log[today_str] = sent_today
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print("로그 저장 완료")
else:
    print("현재 알림 시간이 아니거나 이미 전송됨.")
