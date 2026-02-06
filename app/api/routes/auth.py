from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.models import user
from app.models.refresh_tokens import RefreshToken
from app.models.user import User
from app.core.security import verify_password, create_access_token, hash_password
from app.core.refresh import  create_refresh_token
from app.schemas.refresh import RefreshRequest
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession 

from app.core.refresh import create_refresh_token, revoke_refresh_token
from app.services.auth_service import authenticate_user
from app.services.exceptions import AccountLocked, InvalidCredentials 

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user_in.email.lower()

    result = await db.execute(
        select(User).where(User.email == email))
    
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, hashed_password=hash_password(user_in.password))

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user



@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):

    try:
        user = await authenticate_user(
            db,
            form_data.username,
            form_data.password,
        )
    except AccountLocked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked. Try again later.",
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    assert user is not None
    
    # Create Access Token
    access_token = create_access_token(subject=str(user.id))

    # Create Refresh Token in Redis
    refresh_token = await create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshRequest):
    """
    Revokes the provided refresh token.
    """
    success = await revoke_refresh_token(data.refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found or already revoked"
        )
    return None