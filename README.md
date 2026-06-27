# Talkio

```
talkio/
├── backend/              Python (FastAPI)
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── main.py          FastAPI 앱 + 라우터 등록
│       ├── db.py            SQLite 연결 + 스키마 초기화 + 시드
│       ├── schema.sql       users / connections 테이블
│       ├── schemas.py       Pydantic 요청/응답 모델
│       ├── routers/
│       │   ├── auth.py          POST /api/auth/login (+ get_current_user)
│       │   ├── profile.py       GET /api/me, /api/me/qr, /api/c/{token}
│       │   ├── connections.py   POST·GET /api/connections
│       │   ├── nudges.py        ★ GET /api/nudges
│       │   └── transcribe.py    POST /api/transcribe (Whisper)
│       └── services/
│           └── ai.py        OpenAI 호출 (nudge 생성 + 전사)
└── frontend/             React + Vite
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx
        └── App.jsx
```

## 실행 (backend)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```

