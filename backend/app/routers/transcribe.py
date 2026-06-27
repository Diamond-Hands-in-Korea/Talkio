"""음성 → 텍스트 전사 (Whisper). 부가 기능.

전사 결과는 커넥션 memo(대화 하이라이트)로 사용. memo 직접 입력 fallback 항상 유지.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.routers.auth import get_current_user
from app.schemas import TranscribeResponse
from app.services.ai import transcribe_audio

router = APIRouter(prefix="/api", tags=["transcribe"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    _user=Depends(get_current_user),
):
    """오디오 파일 업로드 → 텍스트. 전사 실패 시 502 (프론트는 memo 직접 입력으로 폴백)."""
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="empty_file")

    try:
        text = transcribe_audio(audio_bytes, file.filename or "audio.m4a")
    except Exception:
        raise HTTPException(status_code=502, detail="transcribe_failed")

    return TranscribeResponse(text=text)
