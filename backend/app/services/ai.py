"""OpenAI 호출 모음 — 여기만 "로직". (generate_nudges 담당: 태은)

두 함수는 서로 독립적. (nudge 가 transcribe 에 의존하지 않게 유지)
"""

import json
import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _fallback_reason(c: dict) -> str:
    """LLM 없이도 보여줄 룰 기반 이유."""
    days = c.get("days_since")
    event = c.get("event_name")
    base = f"마지막으로 만난 지 {days}일이 지났어요." if days is not None else "한동안 연락이 뜸했어요."
    if event:
        base += f" {event}에서 나눈 대화를 이어가 보세요."
    return base


def generate_nudges(me: dict, connections: list[dict]) -> list[dict]:
    """내 프로필 + 커넥션들 → 후속 연락 추천 + 메시지 초안.

    반환: [{connection_id, name, reason, draft_message}, ...]
    LLM 호출이 실패해도 예외를 던지지 않고 draft_message=None 폴백으로 채운다.
    """
    if not connections:
        return []

    # 폴백(LLM 실패/키 없음 시 그대로 반환할 기본값)
    fallback = [
        {
            "connection_id": c["connection_id"],
            "name": c.get("name"),
            "reason": _fallback_reason(c),
            "draft_message": None,
        }
        for c in connections
    ]

    try:
        from openai import OpenAI

        client = OpenAI()  # OPENAI_API_KEY 는 .env 에서 로드

        system = (
            "너는 네트워킹 관계 관리 비서다. 사용자가 이벤트에서 만난 사람들 중 "
            "지금 다시 연락하면 좋을 후보가 주어진다. 각 후보에 대해 (1)왜 지금 "
            "연락하면 좋은지 이유와 (2)상대에게 바로 보낼 수 있는 자연스러운 한국어 "
            "후속 메시지 초안을 작성하라. 사용자의 네트워킹 목표와 둘이 나눈 대화 "
            "메모를 근거로 개인화하라. 반드시 JSON 으로만 답하라."
        )
        payload = {
            "me": me,
            "connections": [
                {
                    "connection_id": c["connection_id"],
                    "name": c.get("name"),
                    "background": c.get("background"),
                    "demographic": c.get("demographic"),
                    "event_name": c.get("event_name"),
                    "memo": c.get("memo"),
                    "days_since_met": c.get("days_since"),
                }
                for c in connections
            ],
        }
        user = (
            "다음 컨텍스트를 보고 각 connection 에 대한 추천을 생성하라.\n"
            + json.dumps(payload, ensure_ascii=False)
            + '\n\n출력 형식: {"nudges": [{"connection_id": <int>, '
            '"reason": "<한국어 이유>", "draft_message": "<한국어 메시지 초안>"}]}'
        )

        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        data = json.loads(resp.choices[0].message.content)
        by_id = {item["connection_id"]: item for item in data.get("nudges", [])}

        result = []
        for c in connections:
            item = by_id.get(c["connection_id"])
            if item and item.get("reason"):
                result.append(
                    {
                        "connection_id": c["connection_id"],
                        "name": c.get("name"),
                        "reason": item["reason"],
                        "draft_message": item.get("draft_message"),
                    }
                )
            else:
                # 이 후보만 LLM 결과 누락 → 폴백
                result.append(
                    {
                        "connection_id": c["connection_id"],
                        "name": c.get("name"),
                        "reason": _fallback_reason(c),
                        "draft_message": None,
                    }
                )
        return result
    except Exception:
        # LLM 호출 실패 — 데모가 빈 화면으로 죽지 않도록 룰 기반 폴백 반환.
        return fallback


def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """오디오 → 텍스트 (Whisper)."""
    # TODO: client.audio.transcriptions.create(model="whisper-1", file=...)
    raise NotImplementedError
