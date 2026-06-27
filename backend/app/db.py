import sqlite3
from pathlib import Path

# talkio.db 는 backend/ 루트에 생성 (.gitignore 처리됨)
DB_PATH = Path(__file__).resolve().parent.parent / "talkio.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """FastAPI 의존성: 요청마다 커넥션 열고 닫기."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """앱 시작 시 테이블 생성 + 데모 시드 삽입."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
        _seed(conn)
    finally:
        conn.close()


def _seed(conn: sqlite3.Connection) -> None:
    """데모용 하드코딩 시드 — 로그인 계정(alice) + 커넥션 3건(메모 포함).

    ⚠️ 임시 데모 데이터 (담당: seed 담당자가 검토·교체).
    재실행해도 중복되지 않도록 INSERT OR IGNORE 사용.
    met_at 을 과거로 깔아 nudge 후보(기본 7일 경과)가 실제로 잡히게 한다.
    """
    users = [
        # email, password, name, contact, demographic, background, networking_goal, share_token
        ("alice@demo.dev", "pw", "김앨리스", "alice@demo.dev", "창업가",
         "B2B SaaS 스타트업 창업가. 초기 팀 빌딩 중.",
         "초기 투자자와 백엔드 엔지니어를 만나고 싶다.", "share_alice"),
        ("bob@demo.dev", "pw", "박밥", "bob@demo.dev / @bob_dev", "직장인",
         "핀테크 백엔드 엔지니어 7년차. 결제·이벤트 소싱 전문.",
         "사이드 프로젝트 동료를 찾는 중.", "share_bob"),
        ("carol@demo.dev", "pw", "이캐롤", "carol@vc.example", "투자자",
         "시드 단계 전문 엔젤 투자자.",
         "초기 SaaS 창업가를 발굴하고 싶다.", "share_carol"),
        ("dave@demo.dev", "pw", "최데이브", "dave@demo.dev", "대학생",
         "컴퓨터공학 4학년, ML 관심.",
         "인턴십과 멘토를 찾는 중.", "share_dave"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO users "
        "(email, password, name, contact, demographic, background, networking_goal, share_token) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        users,
    )
    conn.commit()

    def uid(email: str) -> int:
        return conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]

    alice, bob, carol, dave = (uid("alice@demo.dev"), uid("bob@demo.dev"),
                               uid("carol@demo.dev"), uid("dave@demo.dev"))

    connections = [
        # owner, contact, event_name, memo, days_ago
        (alice, bob, "Cursor Seoul Hackathon #3",
         "결제 시스템 확장 얘기. 둘 다 이벤트 소싱에 관심. 다음에 아키텍처 더 깊게 얘기하기로 함.", 10),
        (alice, carol, "AI Founders Meetup",
         "시드 라운드 준비 중이라 했더니 피치덱 보고 싶다고 함. 후속으로 덱 공유 약속.", 3),
        (alice, dave, "대학 창업 동아리 데모데이",
         "ML 인턴 자리 찾는다길래 우리 팀 소개함. 포트폴리오 받기로 함.", 20),
    ]
    for owner, contact, event, memo, days_ago in connections:
        conn.execute(
            "INSERT OR IGNORE INTO connections "
            "(owner_id, contact_user_id, event_name, memo, met_at) "
            "VALUES (?, ?, ?, ?, datetime('now', ?))",
            (owner, contact, event, memo, f"-{days_ago} days"),
        )
    conn.commit()
