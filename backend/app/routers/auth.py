"""인증: 하드코딩 계정 로그인 + 현재 유저 의존성.

⚠️ 데모/로컬 테스트용 임시 구현 (담당: auth 담당자가 검토·교체).
   토큰 스킴은 단순 `tok_{user_id}` — 만료/서명 없음(해커톤 한정).
   다른 라우터(connections, nudges)가 의존하는 계약:
     get_current_user → Authorization: Bearer 토큰 검증 → 현재 유저 row 반환,
                        없거나 무효면 401.
"""

import sqlite3

from fastapi import APIRouter, Depends, Header, HTTPException

from app.db import get_db
from app.schemas import LoginRequest

router = APIRouter(prefix="/api", tags=["auth"])

TOKEN_PREFIX = "tok_"


@router.post("/auth/login")
def login(body: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    """하드코딩(시드) 계정 검증 → 단순 토큰 발급."""
    row = db.execute(
        "SELECT id FROM users WHERE email = ? AND password = ?",
        (body.email, body.password),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="invalid_credentials")
    return {"user_id": row["id"], "token": f"{TOKEN_PREFIX}{row['id']}"}


def get_current_user(
    authorization: str = Header(None),
    db: sqlite3.Connection = Depends(get_db),
) -> sqlite3.Row:
    """Authorization: Bearer tok_{id} → users row. 무효 시 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")

    token = authorization[len("Bearer "):].strip()
    if not token.startswith(TOKEN_PREFIX):
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        user_id = int(token[len(TOKEN_PREFIX):])
    except ValueError:
        raise HTTPException(status_code=401, detail="unauthorized")

    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    return row
