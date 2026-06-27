"""커넥션: 생성(이벤트·메모) + 목록. (담당: )"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["connections"])


# TODO: POST /api/connections  → 커넥션 생성 (contact_token, event_name, memo)
# TODO: GET  /api/connections  → 내 커넥션 목록 (상대 프로필 + event + memo)
