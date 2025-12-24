"""FastAPI app exposing the CV name ↔ email verification endpoint."""
from fastapi import FastAPI

from .schemas import VerificationRequest, VerificationResponse
from .service import EmailVerificationService

app = FastAPI(title="CV Name ↔ Email Verification Service")
service = EmailVerificationService()


@app.post("/validate-cv-email", response_model=VerificationResponse)
async def validate_cv_email(payload: VerificationRequest) -> VerificationResponse:
    result = service.verify(payload.full_name, payload.email, debug=payload.debug)
    return VerificationResponse(**result)
