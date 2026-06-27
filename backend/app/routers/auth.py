"""인증: 하드코딩 계정 로그인 + 현재 유저 의존성. (담당: )"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["auth"])


# TODO: POST /api/auth/login  → 단순 토큰 발급 (예: "tok_{user_id}")
# TODO: get_current_user 의존성 — Authorization 헤더의 토큰 → users row
