"""Request/response schemas for FastAPI."""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class VerificationRequest(BaseModel):
    full_name: str = Field(..., description="Full name from CV")
    email: Optional[EmailStr] = Field(None, description="Email address to verify")
    debug: bool = Field(False, description="Include debug info")


class VerificationResponse(BaseModel):
    email: Optional[EmailStr]
    decision: str
    confidence: int
    reason: str
    debug: Optional[dict] = None
