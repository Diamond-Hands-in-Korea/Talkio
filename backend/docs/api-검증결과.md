# API 동적 검증 결과 (LinkUp / Talkio 백엔드)

> 실제 서버를 기동하고 모든 엔드포인트를 `curl`로 전수 호출하여 설계 기능과 대조한 결과입니다.
> `api-verification` 스킬 절차에 따라 수행했습니다.

## 1. 검증 환경

| 항목 | 값 |
|---|---|
| 대상 브랜치 | `dev` (HEAD `b0506e9`, PR #2 머지 후) |
| 실행 | `uvicorn app.main:app` (127.0.0.1:8011) |
| Python | 3.9.6 (venv) |
| DB | SQLite `talkio.db` (기동 시 시드 자동 삽입, 검증 전 초기화) |
| OpenAI | `OPENAI_API_KEY` 적용 — 넛지 AI 초안 실호출 검증 (모델: `gpt-4o-mini`) |

검증 일자: 2026-06-27

> 참고: `backend/docs/설계문서.md`는 빈 파일(0바이트)이라, 합의된 기능 목록을 스펙으로 삼아 대조했습니다.

## 2. 시드 데이터 (데모 하드코딩)

- 계정 4명: `alice@demo.dev` / `bob@demo.dev` / `carol@demo.dev` / `dave@demo.dev` (공통 비밀번호 `pw`)
- 토큰 스킴: 로그인 토큰 `tok_{user_id}`, 공유 토큰 `share_{name}`
- alice 소유 커넥션 3건 (met_at: 박밥 10일 전 / 캐롤 3일 전 / 데이브 20일 전, 메모 포함)

## 3. 엔드포인트 전수 검증 결과

| Step | 설계 기능 | API | 예상 | 실제 | 결과 |
|---|---|---|---|---|---|
| 1 | 로그인(하드코딩) | `POST /api/auth/login` | 200 + `{user_id, token}` | `200 {user_id:1, token:"tok_1"}` | ✅ |
| 1b | 로그인 실패 | `POST /api/auth/login` (오답 비번) | 401 | `401 {"error":"invalid_credentials"}` | ✅ |
| 2 | 내 프로필(이름·연락처·데모그래픽·배경·네트워킹목표) | `GET /api/me` | 200, 5개 필드 | 5개 필드 전부 반환 | ✅ |
| 2b | 인증 누락 | `GET /api/me` (토큰 없음) | 401 | `401 {"error":"unauthorized"}` | ✅ |
| 3 | 내 프로필 QR 발급 | `GET /api/me/qr` | `{share_url, token}` | `http://localhost:5173/c/share_alice` | ✅ |
| 4 | QR 스캔 → 공개 프로필 공유 | `GET /api/c/{token}` | 200, 공개 프로필(무인증) | 박밥 공개 프로필 반환 | ✅ |
| 4b | 잘못된 공유 토큰 | `GET /api/c/NOPE` | 404 | `404 {"error":"invalid_token"}` | ✅ |
| 5 | 스캔 → 커넥션 생성 | `POST /api/connections` | 201 | `201 {connection_id:4, ...}` | ✅ |
| 5b | 인증 누락 | `POST /api/connections` | 401 | `401 {"error":"unauthorized"}` | ✅ |
| 5c | 잘못된 대상 토큰 | `POST /api/connections` | 404 | `404 {"error":"invalid_token"}` | ✅ |
| 6 | 커넥션 목록(상대 프로필+이벤트+메모) | `GET /api/connections` | 200, 목록 | alice 커넥션 3건 정상 | ✅ |
| 7 | ★ 추천 목록 + 이유 | `GET /api/nudges` | 후보+이유 | 7일 경과 후보 2건(박밥·데이브), 이유 생성 | ✅ |
| 7b | ★ AI 맞춤 메시지 초안 | `GET /api/nudges` | `draft_message` 채워짐 | 개인화된 한국어 초안 생성됨 | ✅ |
| 8 | 음성 전사 | `POST /api/transcribe` | 200 + `{text}` | 한국어 오디오 정확히 전사 | ✅ |
| 8b | 전사 무인증 | `POST /api/transcribe` | 401 | `401 {"error":"unauthorized"}` | ✅ |
| 8c | 전사 파일 누락 | `POST /api/transcribe` | 422 | `422 Field required` | ✅ |

## 4. ★ 핵심 기능(AI 넛지) 상세

`GET /api/nudges`는 설계대로 동작합니다.

- **후보 선정**: `met_at` 기준 7일 이상 경과한 커넥션만 추천 → 박밥(10일), 데이브(20일) 선정, 캐롤(3일) 정상 제외.
- **개인화 근거**: 내 프로필 + 네트워킹 목표 + 커넥션 배경 + **대화 메모(하이라이트)**를 LLM에 전달.
- **AI 초안 검증 결과 예시**(키 적용 후 실호출):
  - 최데이브 → *"…데모데이에서 이야기한 대로 포트폴리오 잘 받았습니다. 우리 팀에 ML 분야에 도움이 될 아이디어가…"* (메모의 포트폴리오·ML 반영)
  - 박밥 → *"…해커톤에서 이야기한 것처럼 결제 시스템 확장에 대해 더 깊이 논의해보고 싶어요…"* (메모의 결제 시스템 확장 반영)
- **폴백 안정성**: `OPENAI_API_KEY`가 없으면 예외를 던지지 않고 룰 기반 `reason` + `draft_message=null`로 폴백하여 데모가 죽지 않음 (키 없는 환경에서 별도 확인).

## 5. 음성 전사(Whisper) 상세

`POST /api/transcribe`는 설계대로 동작합니다 (인증 필요, 실패 시 502 폴백).

- 입력: macOS `say`로 생성한 한국어 음성(wav, 16kHz).
- 전사 결과: *"안녕하세요. 이것은 토키오 음성 전사 테스트입니다. 결제 시스템 확장에 대해 이야기 했습니다."* → 원문과 일치.
- 모델: `whisper-1` (`WHISPER_MODEL` 환경변수로 교체 가능).
- 실패 처리: `OPENAI_API_KEY` 없음/Whisper 실패 시 `502 transcribe_failed` 반환 → 프론트는 memo 직접 입력으로 폴백.

## 6. 미해결 / 범위 밖

| 항목 | 상태 | 비고 |
|---|---|---|
| `설계문서.md` | ⚠️ 빈 파일 | 0바이트. 합의된 기능 목록으로 대조함 |

## 7. 결론

- 설계 핵심 기능(로그인·프로필·QR·공개프로필·커넥션·메모·AI 추천+초안) + 부가 기능(음성 전사) **전부 실서버에서 동작 확인 완료**.
- 정상/예외(401·404·422·502) 시나리오 모두 설계대로 응답.
- **미구현 기능 없음.**
