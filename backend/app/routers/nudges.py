"""★ AI 후속 연락 추천 + 맞춤 메시지 초안. (담당: 태은)

내 프로필 + 커넥션 + 메모(하이라이트) + 네트워킹 목표 → services.ai.generate_nudges
후보 = met_at 이 N일(기본 7) 이상 지난 커넥션. (테이블에 last_contacted_at 이 없어 met_at 사용)
LLM 실패해도 200 — generate_nudges 가 draft=null 폴백을 보장한다.
"""

import sqlite3

from fastapi import APIRouter, Depends, Query

from app.db import get_db
from app.routers.auth import get_current_user
from app.schemas import Nudge, NudgeList
from app.services.ai import generate_nudges

router = APIRouter(prefix="/api", tags=["nudges"])


@router.get("/nudges", response_model=NudgeList)
def list_nudges(
    days: int = Query(7, ge=0, description="후보 기준 경과일(met_at 기준)"),
    limit: int = Query(5, ge=1, le=20, description="최대 추천 수"),
    me=Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    rows = db.execute(
        """
        SELECT c.id          AS connection_id,
               u.name        AS name,
               u.background  AS background,
               u.demographic AS demographic,
               c.event_name  AS event_name,
               c.memo        AS memo,
               c.met_at      AS met_at,
               CAST(julianday('now') - julianday(c.met_at) AS INTEGER) AS days_since
        FROM connections c
        JOIN users u ON u.id = c.contact_user_id
        WHERE c.owner_id = ?
          AND julianday('now') - julianday(c.met_at) >= ?
        ORDER BY days_since DESC
        LIMIT ?
        """,
        (me["id"], days, limit),
    ).fetchall()

    me_profile = {
        "name": me["name"],
        "background": me["background"] if "background" in me.keys() else None,
        "networking_goal": me["networking_goal"] if "networking_goal" in me.keys() else None,
    }
    candidates = [dict(r) for r in rows]

    nudges = generate_nudges(me_profile, candidates)
    return NudgeList(nudges=[Nudge(**n) for n in nudges])
