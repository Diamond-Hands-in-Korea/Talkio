"""Pydantic 요청/응답 모델. (프론트와의 계약 — 초반에 같이 확정)

담당 분담:
  - LoginRequest / LoginResponse        (auth)        ← 다른 담당자
  - Profile / QRResponse                (profile me)  ← 다른 담당자
  - PublicProfile                       (profile c)   ← 내 담당
  - ConnectionCreate / ConnectionCreated / ConnectionItem / ConnectionList  (connections) ← 내 담당
  - Nudge / NudgeList                   (nudges)      ← 내 담당
  - TranscribeResponse                  (transcribe)  ← 다른 담당자

DB 컬럼은 `id` 지만 프론트 계약은 `user_id` 로 노출한다(노션 5장 기준).
"""

from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


# --- profile: GET /api/c/{token} (공개 프로필, 민감정보 제외) ---


class PublicProfile(BaseModel):
    user_id: int
    name: str
    background: Optional[str] = None
    demographic: Optional[str] = None
    contact: Optional[str] = None


# --- profile: GET /api/me (내 프로필, networking_goal 포함) ---


class Profile(BaseModel):
    user_id: int
    name: str
    background: Optional[str] = None
    demographic: Optional[str] = None
    contact: Optional[str] = None
    networking_goal: Optional[str] = None


# --- profile: GET /api/me/qr (공유 URL + 토큰) ---


class QRResponse(BaseModel):
    share_url: str
    token: str


# --- connections: POST /api/connections ---


class ConnectionCreate(BaseModel):
    target_token: str          # 스캔으로 얻은 상대의 share_token
    event_name: Optional[str] = None
    memo: Optional[str] = None


class ConnectionCreated(BaseModel):
    connection_id: int
    contact_user_id: int
    event_name: Optional[str] = None
    met_at: str


# --- connections: GET /api/connections ---


class ConnectionItem(BaseModel):
    connection_id: int
    contact_user_id: int
    name: str
    background: Optional[str] = None
    event_name: Optional[str] = None
    memo: Optional[str] = None
    met_at: str
    created_at: str


class ConnectionList(BaseModel):
    connections: list[ConnectionItem]


# --- nudges: GET /api/nudges (★ 핵심) ---


class Nudge(BaseModel):
    connection_id: int
    name: str
    reason: str
    draft_message: Optional[str] = None   # LLM 실패 시 폴백으로 null


class NudgeList(BaseModel):
    nudges: list[Nudge]


# --- transcribe: POST /api/transcribe (음성 → 텍스트) ---


class TranscribeResponse(BaseModel):
    text: str
