"""프로필: 내 프로필 / QR / 공개 프로필."""

import os
import sqlite3

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.db import get_db
from app.routers.auth import get_current_user
from app.schemas import Profile, PublicProfile, QRResponse

router = APIRouter(prefix="/api", tags=["profile"])

# QR 에 인코딩할 프론트 베이스 URL. 데모에선 .env 의 APP_BASE_URL 또는 기본값.
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5173")


@router.get("/me", response_model=Profile)
def get_me(user: sqlite3.Row = Depends(get_current_user)):
    """로그인한 본인의 프로필(네트워킹 목표 포함)."""
    return Profile(
        user_id=user["id"],
        name=user["name"],
        background=user["background"],
        demographic=user["demographic"],
        contact=user["contact"],
        networking_goal=user["networking_goal"],
    )


@router.get("/me/qr", response_model=QRResponse)
def get_my_qr(user: sqlite3.Row = Depends(get_current_user)):
    """내 공개 프로필로 연결되는 공유 URL + 토큰."""
    token = user["share_token"]
    return QRResponse(
        share_url=f"{APP_BASE_URL}/c/{token}",
        token=token,
    )


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
