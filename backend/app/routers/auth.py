from fastapi import APIRouter, HTTPException, Depends, status, Header
from typing import Optional
import jwt
from backend.app.schemas import UserRegister, UserLogin, GoogleAuthRequest, TokenResponse, UserResponse
from backend.app.database import (
    get_user_by_email,
    get_user_by_id,
    create_local_user,
    create_or_get_google_user,
    check_profile_completed
)
from backend.app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to extract and validate current authenticated user from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing or invalid format (expected: Bearer <token>)"
        )
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired. Please log in again."
        )
    
    user_id = int(payload["sub"])
    try:
        user = get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error while fetching user profile: {str(e)}"
        )
        
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")
    return user


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister):
    """Register a new student user using email and password."""
    try:
        existing_user = get_user_by_email(user_data.email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}. Please check DB credentials in .env."
        )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please log in."
        )

    hashed_pw = hash_password(user_data.password)
    try:
        user_id = create_local_user(user_data.full_name, user_data.email, hashed_pw)
        created_user = get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account: {str(e)}"
        )

    token = create_access_token({"sub": str(user_id), "email": created_user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": created_user,
        "is_profile_completed": False,
        "message": "Account created successfully! Please complete your profile."
    }


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    """Authenticate student with email and password."""
    try:
        user = get_user_by_email(credentials.email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}. Please check DB credentials in .env."
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # If the user only signed up via Google
    if user.get("auth_provider") == "google" and not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account was created with Google. Please use 'Continue with Google'."
        )

    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Check profile completion status
    is_completed = check_profile_completed(user["id"])

    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    user_info = {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "auth_provider": user["auth_provider"],
        "avatar_url": user.get("avatar_url"),
        "created_at": user.get("created_at")
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_info,
        "is_profile_completed": is_completed,
        "message": "Logged in successfully!"
    }


@router.post("/google", response_model=TokenResponse)
def google_auth(payload: GoogleAuthRequest):
    """Authenticate or register student using Google OAuth."""
    email = payload.email
    full_name = payload.name or "Techie Student"
    google_id = payload.google_id or ""
    avatar_url = payload.avatar_url

    # If raw credential JWT was passed from Google GIS library, decode claims
    if payload.credential:
        try:
            # Decode unverified claims (in production, verify with Google's public certs / google-auth library)
            unverified_claims = jwt.decode(payload.credential, options={"verify_signature": False})
            email = unverified_claims.get("email", email)
            full_name = unverified_claims.get("name", full_name)
            google_id = unverified_claims.get("sub", google_id)
            avatar_url = unverified_claims.get("picture", avatar_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Google credential token: {str(e)}"
            )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication failed to provide a valid email."
        )

    try:
        user = create_or_get_google_user(
            email=email,
            full_name=full_name,
            google_id=google_id,
            avatar_url=avatar_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error during Google authentication: {str(e)}"
        )

    is_completed = check_profile_completed(user["id"])

    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    user_info = {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "auth_provider": user.get("auth_provider", "google"),
        "avatar_url": user.get("avatar_url"),
        "created_at": user.get("created_at")
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_info,
        "is_profile_completed": is_completed,
        "message": "Google authentication successful!"
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Fetch profile of currently logged-in student."""
    return current_user
