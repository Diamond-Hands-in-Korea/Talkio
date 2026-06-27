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
    """앱 시작 시 테이블 생성. (시드는 담당자가 채우기)"""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
        # TODO(seed): 하드코딩 시드 데이터 삽입 — users 3~4명 + connections + memo
    finally:
        conn.close()
