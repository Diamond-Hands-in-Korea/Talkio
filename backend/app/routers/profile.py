"""프로필: 내 프로필 / QR / 공개 프로필. (담당: 태은 — 공개 프로필만)"""

import sqlite3

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.db import get_db
from app.schemas import PublicProfile

router = APIRouter(prefix="/api", tags=["profile"])


# TODO(다른 담당자): GET /api/me     → 내 프로필 (get_current_user)
# TODO(다른 담당자): GET /api/me/qr  → { share_url, token }  (token = users.share_token)


@router.get("/c/{token}", response_model=PublicProfile)
def public_profile(token: str, db: sqlite3.Connection = Depends(get_db)):
    """QR 스캔 후 열리는 엔드포인트. 토큰 주인의 공개 프로필만 반환(인증 불필요)."""
    row = db.execute(
        "SELECT id, name, background, demographic, contact "
        "FROM users WHERE share_token = ?",
        (token,),
    ).fetchone()

    if row is None:
        return JSONResponse(status_code=404, content={"error": "invalid_token"})

    return PublicProfile(
        user_id=row["id"],
        name=row["name"],
        background=row["background"],
        demographic=row["demographic"],
        contact=row["contact"],
    )
