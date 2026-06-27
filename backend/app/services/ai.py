"""OpenAI 호출 모음 — 여기만 "로직". (담당: )

두 함수는 서로 독립적. (nudge 가 transcribe 에 의존하지 않게 유지)
"""

# from openai import OpenAI
# client = OpenAI()  # OPENAI_API_KEY 는 .env 에서 로드


def generate_nudges(me: dict, connections: list[dict]) -> list[dict]:
    """내 프로필 + 커넥션들 → 후속 연락 추천 + 메시지 초안."""
    # TODO: 프롬프트 구성 → client.chat.completions.create(...) → 파싱
    raise NotImplementedError


def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """오디오 → 텍스트 (Whisper)."""
    # TODO: client.audio.transcriptions.create(model="whisper-1", file=...)
    raise NotImplementedError
