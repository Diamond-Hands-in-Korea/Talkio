-- 1. 사용자 (프로필 = 디지털 명함). 데모는 하드코딩/시드.
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT UNIQUE NOT NULL,   -- 로그인 ID
    password        TEXT NOT NULL,          -- 데모용 평문(해커톤 한정)
    name            TEXT NOT NULL,
    contact         TEXT,                   -- 전화/이메일/링크
    demographic     TEXT,                   -- '대학생' | '직장인' | '창업가' 등
    background      TEXT,                   -- 본인 배경/소개
    networking_goal TEXT,                   -- 네트워킹 목표 (nudge 핵심 입력)
    share_token     TEXT UNIQUE NOT NULL,   -- QR/공개프로필 토큰
    created_at      TEXT DEFAULT (datetime('now'))
);

-- 2. 커넥션 (owner = 나, contact_user = 만난 사람)
CREATE TABLE IF NOT EXISTS connections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id        INTEGER NOT NULL REFERENCES users(id),
    contact_user_id INTEGER NOT NULL REFERENCES users(id),
    event_name      TEXT,                   -- 만난 이벤트
    memo            TEXT,                   -- 나눈 대화/하이라이트
    met_at          TEXT DEFAULT (datetime('now')),
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(owner_id, contact_user_id)       -- 같은 사람 중복 방지
);
