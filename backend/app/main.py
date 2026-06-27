from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

from app.db import init_db
from app.routers import auth, profile, connections, nudges, transcribe

load_dotenv()

app = FastAPI(title="LinkUp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
def _error_format(request, exc: StarletteHTTPException):
    """전역 에러 포맷 통일: { "error": "<코드>" } (문서 5장)."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True}


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(connections.router)
app.include_router(nudges.router)
app.include_router(transcribe.router)
