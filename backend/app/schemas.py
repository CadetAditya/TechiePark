from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120, description="User's full name")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password (at least 6 characters)")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = Field(None, description="Google OAuth ID Token JWT")
    email: Optional[EmailStr] = Field(None, description="Google account email (fallback/dev)")
    name: Optional[str] = Field(None, description="Google account display name")
    google_id: Optional[str] = Field(None, description="Google sub ID")
    avatar_url: Optional[str] = Field(None, description="Google profile picture URL")

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    auth_provider: str
    avatar_url: Optional[str] = None
    created_at: Optional[Any] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_profile_completed: bool = False
    message: str = "Authentication successful"

