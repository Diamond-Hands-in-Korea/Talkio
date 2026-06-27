"""Pydantic 요청/응답 모델. (프론트와의 계약 — 초반에 같이 확정)

TODO: 아래 모델들 채우기. 엔드포인트별 담당자가 자기 모델 정의.
  - LoginRequest / LoginResponse        (auth)
  - Profile / QRResponse / PublicProfile (profile)
  - ConnectionCreate / ConnectionOut     (connections)
  - Nudge                                (nudges)
  - TranscribeResponse                   (transcribe)
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str
