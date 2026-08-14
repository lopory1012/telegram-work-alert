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

# 실참 누적 대상 방 (투표를 올릴 실제 방)
MISSION_CHAT_ID = "-1001940900666"   # 전도단 방
MISSION_CHAT_SLUG = "1940900666"     # 링크 생성용

EDU_CHAT_ID = "-1003809710264"       # 신앙교육 방
EDU_CHAT_SLUG = "3809710264"         # 링크 생성용

now = datetime.now(ZoneInfo("Asia/Seoul"))
weekday = now.weekday()  # 월=0, 화=1, 수=2, 목=3, 금=4, 토=5, 일=6
now_total = now.hour * 60 + now.minute
today_str = now.strftime("%Y-%m-%d")


def in_window(h, m):
    return abs(now_total - (h * 60 + m)) <= TOLERANCE


def api_call(method, payload):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
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
        "options": json.dumps(["참석✅", "불참❌"], ensure_ascii=False),
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
if isinstance(sent_today, list):  # 이전 버전 로그 호환
    sent_today = {k: True for k in sent_today}

message = None       # 개인 알림방으로 보낼 메시지
key = None            # 오늘 전송 기록용 key

poll_room_chat_id = None   # 실제 방에 투표/리마인드 보낼 대상
poll_question = None       # 새 투표를 만들 때 사용할 질문
poll_log_key = None        # 그 투표의 message_id를 저장/조회할 키
poll_slug = None           # 링크 생성용 채팅방 번호
reminder_text = None       # 이미 투표가 있을 때 보낼 리마인드 문구


if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
    message = "🔔 테스트 알림입니다.\n텔레그램 봇이 정상적으로 연결되었습니다."

else:
    # ── 기존 취합 알림 ──────────────────────────
    if in_window(23, 50) and "daily" not in sent_today:
        message = "🔔 일일보고 작성 시간입니다.\nhttps://t.me/c/3879535253/14"
        key = "daily"
    elif weekday == 6 and in_window(21, 50) and "sun" not in sent_today:
        message = "🔔 신앙관리교육 사전취합 시간입니다.\nhttps://t.me/c/3809710264/3"
        key = "sun"
    elif weekday == 0 and in_window(21, 50) and "mon" not in sent_today:
        message = "🔔 수요일 사전예배 사전취합 시간입니다.\nhttps://t.me/c/2817611748/5580"
        key = "mon"
    elif weekday == 3 and in_window(21, 50) and "thu" not in sent_today:
        message = "🔔 구역예배 취합 시간입니다.\nhttps://t.me/abcde0156"
        key = "thu"
    elif weekday == 4 and in_window(21, 50) and "fri" not in sent_today:
        message = (
            "🔔 전도단 사전취합 / 주일예배 사전취합 시간입니다.\n"
            "전도단: https://t.me/c/1940900666/11868\n"
            "주일예배: https://t.me/c/2817611748/5580"
        )
        key = "fri"

    # ── 기도회 안내 (일/월/수/목/금 22시) ──────────
    elif weekday in (6, 0, 2, 3, 4) and in_window(22, 0) and "pray_reminder" not in sent_today:
        message = "🙏 내일은 오전 7시 기도회가 있는 날입니다. 함께 기도합시다.\nhttps://t.me/suwon_gather_bot"
        key = "pray_reminder"

    # ── 전도단 실참 누적 (금 10/17/20/22시) ────────
    elif weekday == 4 and in_window(10, 0) and "mission_10" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!\nhttps://t.me/c/1940900666/11868"
        key = "mission_10"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_question = "[전도단] 오늘 실참 체크해주세요"
        poll_log_key = "mission_poll"
        poll_slug = MISSION_CHAT_SLUG
    elif weekday == 4 and in_window(17, 0) and "mission_17" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!\nhttps://t.me/c/1940900666/11868"
        key = "mission_17"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_log_key = "mission_poll"
        poll_slug = MISSION_CHAT_SLUG
        reminder_text = "⏰ 아직 실참 체크 안 하신 분은 위 투표에서 참석✅ 눌러주세요!"
    elif weekday == 4 and in_window(20, 0) and "mission_20" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!\nhttps://t.me/c/1940900666/11868"
        key = "mission_20"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_log_key = "mission_poll"
        poll_slug = MISSION_CHAT_SLUG
        reminder_text = "⏰ 아직 실참 체크 안 하신 분은 위 투표에서 참석✅ 눌러주세요!"
    elif weekday == 4 and in_window(22, 0) and "mission_22" not in sent_today:
        message = "📋 전도단 실참 누적 해주세요!\nhttps://t.me/c/1940900666/11868"
        key = "mission_22"
        poll_room_chat_id = MISSION_CHAT_ID
        poll_log_key = "mission_poll"
        poll_slug = MISSION_CHAT_SLUG
        reminder_text = "⏰ 아직 실참 체크 안 하신 분은 위 투표에서 참석✅ 눌러주세요!"

    # ── 신앙교육 실참 누적 (화 9:50/17/20/22시) ────
    elif weekday == 1 and in_window(9, 50) and "edu_0950" not in sent_today:
        message = "📋 신앙교육 실참 누적
