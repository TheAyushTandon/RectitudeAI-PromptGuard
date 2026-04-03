"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from backend.models.requests import LoginRequest
from backend.models.responses import TokenResponse
from backend.gateway.security.auth.jwt_handler import JWTHandler
from backend.gateway.config import settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Demo user database (replace with real DB in production)
DEMO_USERS = {
    "demo_user": {
        "username": "demo_user",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$fq815lwrRYgxJkQIofQeow$zQ6btAwncFNiEW6Mj9C6HLSRde7z9xomf2sS/f7x/Aw"
    },
    "admin": {
        "username": "admin",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$vNf6X6tVyvlfSymFEIKwdg$pOD5k5hN+qOI3IIaekPLZSlQFSpuj4+rp5tHlcYsbbE"
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    User login endpoint.
    
    Returns JWT access token for authenticated requests.
    
    **Demo Credentials:**
    - Username: `demo_user`, Password: `demo_password_123`
    - Username: `admin`, Password: `admin_password_123`
    """
    
    user = DEMO_USERS.get(request.username)
    
    is_valid = bool(user and JWTHandler.verify_password(request.password, user["hashed_password"]))
        
    if not is_valid:
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = JWTHandler.create_access_token(
        data={"sub": request.username, "username": request.username},
        expires_delta=timedelta(minutes=settings.jwt_expiration_minutes)
    )
    
    logger.info(f"User logged in: {request.username}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expiration_minutes * 60
    )


@router.post("/register")
async def register(request: LoginRequest):
    """
    User registration endpoint (placeholder).
    
    In production, this would create a new user in the database.
    """
    
    if request.username in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # In production: save to database
    logger.info(f"Registration attempt for user: {request.username}")
    
    return {"message": "Registration successful (demo mode - not persisted)"}