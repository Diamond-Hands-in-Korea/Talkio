"""커넥션: 생성(이벤트·메모) + 목록. (담당: 태은)

인증이 필요한 엔드포인트 — auth.get_current_user 의존.
  계약: get_current_user 는 Authorization: Bearer 토큰을 검증해
        현재 유저 row(sqlite3.Row, 최소 `id` 포함)를 반환하고,
        토큰이 없거나 무효면 401 을 낸다.
"""

import sqlite3

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.db import get_db
from app.routers.auth import get_current_user
from app.schemas import ConnectionCreate, ConnectionCreated, ConnectionItem, ConnectionList

router = APIRouter(prefix="/api", tags=["connections"])


@router.post("/connections", response_model=ConnectionCreated, status_code=201)
def create_connection(
    body: ConnectionCreate,
    me=Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    """스캔한 상대(target_token)와의 커넥션을 이벤트·메모와 함께 생성."""
    owner_id = me["id"]

    target = db.execute(
        "SELECT id FROM users WHERE share_token = ?",
        (body.target_token,),
    ).fetchone()
    if target is None:
        return JSONResponse(status_code=404, content={"error": "invalid_token"})

    contact_user_id = target["id"]

    try:
        cur = db.execute(
            "INSERT INTO connections (owner_id, contact_user_id, event_name, memo) "
            "VALUES (?, ?, ?, ?)",
            (owner_id, contact_user_id, body.event_name, body.memo),
        )
        db.commit()
        connection_id = cur.lastrowid
    except sqlite3.IntegrityError:
        # UNIQUE(owner_id, contact_user_id) — 같은 사람 재스캔 시 기존 커넥션 반환.
        db.rollback()
        connection_id = db.execute(
            "SELECT id FROM connections WHERE owner_id = ? AND contact_user_id = ?",
            (owner_id, contact_user_id),
        ).fetchone()["id"]

    row = db.execute(
        "SELECT id, contact_user_id, event_name, met_at FROM connections WHERE id = ?",
        (connection_id,),
    ).fetchone()

    return ConnectionCreated(
        connection_id=row["id"],
        contact_user_id=row["contact_user_id"],
        event_name=row["event_name"],
        met_at=row["met_at"],
    )


@router.get("/connections", response_model=ConnectionList)
def list_connections(
    me=Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    """내가 소유한 커넥션 목록 — 상대 프로필 + 이벤트 + 메모 + 만난 시각."""
    rows = db.execute(
        """
        SELECT c.id            AS connection_id,
               c.contact_user_id AS contact_user_id,
               u.name          AS name,
               u.background    AS background,
               c.event_name    AS event_name,
               c.memo          AS memo,
               c.met_at        AS met_at,
               c.created_at    AS created_at
        FROM connections c
        JOIN users u ON u.id = c.contact_user_id
        WHERE c.owner_id = ?
        ORDER BY c.met_at DESC
        """,
        (me["id"],),
    ).fetchall()

    return ConnectionList(connections=[ConnectionItem(**dict(r)) for r in rows])
