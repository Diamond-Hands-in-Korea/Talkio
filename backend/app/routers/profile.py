"""프로필: 내 프로필 / QR / 공개 프로필. (담당: )"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["profile"])


# TODO: GET /api/me          → 내 프로필 (get_current_user)
# TODO: GET /api/me/qr       → { share_url, token }  (token = users.share_token)
# TODO: GET /api/c/{token}   → share_token 으로 공개 프로필 조회 (인증 불필요)
