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

# 전도단, 신앙교육 실참 체크 투표는 이제 이 방으로 통합
MISSION_CHAT_ID = "-5144445256"
EDU_CHAT_ID = "-5144445256"

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
