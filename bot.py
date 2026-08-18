# ============================================================
# 투표 생성
# ============================================================

if (
    poll_room_chat_id
    and poll_question
):

    poll_result = send_poll(
        poll_room_chat_id,
        poll_question
    )


    if poll_result.get("ok"):

        poll_id = (
            poll_result["result"]["poll"]["id"]
        )

        log["polls"][poll_id] = {
            "key": poll_key,
            "voters": {}
        }

        sent_today[
            poll_key + "_poll_id"
        ] = poll_id

        print(
            "⭐ 투표 저장:",
            poll_key,
            poll_id
        )

        send_message(
            CHAT_ID,
            poll_question + " 투표가 올라갔습니다."
        )

    did_something = True
