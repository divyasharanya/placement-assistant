"""
Auth Service - Authentication and Authorization
FastAPI-based microservice for user authentication
"""

import os
import sys
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

# Add parent directory to path for database imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
import redis.asyncio as redis
import json
import hashlib

from database.models import User, UserProfile, UserRole, SubscriptionTier

# ==================== Configuration ====================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/aimock")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ==================== Password Hashing ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ==================== JWT Tokens ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ==================== Pydantic Models ====================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    target_role: Optional[str]
    experience_level: Optional[str]
    preferred_languages: Optional[List[str]]
    timezone: Optional[str]
    interview_frequency: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class MFAEnableRequest(BaseModel):
    enable: bool

# ==================== Database Setup ====================

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ==================== Redis Setup ====================

redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

# ==================== OAuth2 Setup ====================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Check if token is in blacklist
    r = await get_redis()
    if await r.get(f"blacklist:{token}"):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="User account is deactivated")
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.email_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    return current_user

# ==================== Rate Limiting ====================

async def check_rate_limit(user_id: str, limit: int = 100, window: int = 3600) -> bool:
    """Check if user has exceeded rate limit"""
    r = await get_redis()
    key = f"rate_limit:{user_id}"
    
    current = await r.get(key)
    if current is None:
        await r.setex(key, window, 1)
        return True
    
    if int(current) >= limit:
        return False
    
    await r.incr(key)
    return True

# ==================== Auth Service ====================

app = FastAPI(title="Auth Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.CANDIDATE,
        subscription_tier=SubscriptionTier.FREE
    )
    
    db.add(user)
    await db.flush()
    
    # Create user profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    
    await db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # TODO: Send verification email in background
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@app.post("/v1/auth/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    # Find user
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="User account is deactivated")
    
    # Check rate limit
    if not await check_rate_limit(str(user.id)):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@app.post("/v1/auth/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(request.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Generate new tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )

@app.post("/v1/auth/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme)
):
    # Add token to blacklist
    r = await get_redis()
    payload = decode_token(token)
    exp = payload.get("exp", 0) if payload else 0
    ttl = max(0, exp - int(datetime.utcnow().timestamp()))
    
    if ttl > 0:
        await r.setex(f"blacklist:{token}", ttl, "1")
    
    return {"message": "Successfully logged out"}

@app.get("/v1/auth/me", response_model=Dict)
async def get_me(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Get profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role.value,
        "subscription_tier": current_user.subscription_tier.value,
        "email_verified": current_user.email_verified,
        "mfa_enabled": current_user.mfa_enabled,
        "profile": profile.dict() if profile else None,
        "created_at": current_user.created_at.isoformat()
    }

@app.put("/v1/auth/me", response_model=Dict)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "User updated successfully"}

@app.post("/v1/auth/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store in Redis with 1 hour expiry
        r = await get_redis()
        await r.setex(f"password_reset:{reset_token}", 3600, str(user.id))
        
        # TODO: Send reset email in background
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a reset link has been sent"}

@app.post("/v1/auth/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    r = await get_redis()
    user_id = await r.get(f"password_reset:{request.token}")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password_hash = get_password_hash(request.new_password)
    user.updated_at = datetime.utcnow()
    await db.commit()
    
    # Delete reset token
    await r.delete(f"password_reset:{request.token}")
    
    return {"message": "Password reset successfully"}

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth"}

# ==================== Run ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
