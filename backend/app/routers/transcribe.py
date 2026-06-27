"""음성 → 텍스트 전사 (Whisper). 부가 기능 — nudge 완성 후. (담당: )

전사 결과는 커넥션 memo(대화 하이라이트)로 사용. memo 직접 입력 fallback 항상 유지.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["transcribe"])


# TODO: POST /api/transcribe  → 오디오 파일 업로드 → services.ai.transcribe_audio → { text }
