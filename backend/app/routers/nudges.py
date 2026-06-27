"""★ AI 후속 연락 추천 + 맞춤 메시지 초안. (담당: )

내 프로필 + 커넥션 + 메모(하이라이트) + 네트워킹 목표 → services.ai.generate_nudges
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["nudges"])


# TODO: GET /api/nudges  → [{ connection_id, contact, reason, draft_message }, ...]
