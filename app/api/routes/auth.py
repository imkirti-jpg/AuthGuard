from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.db.redis import redis_client
from app.models import user, user_roles
from app.models.refresh_tokens import RefreshToken
from app.models.role import Role
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


from app.schemas.user import PasswordResetRequest, PasswordResetConfirm
from app.core.pass_reset import create_reset_token, verify_reset_token, delete_reset_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user_in.email.lower()

    result = await db.execute(
        select(User).where(User.email == email))
    
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, hashed_password=hash_password(user_in.password))

    db.add(user)


    default_role = await db.scalar(
        select(Role).where(Role.name == "user")
    )
    if not default_role:
        raise HTTPException(
            status_code=500,
            detail="Default role not configured",
        )

    await db.execute(
        user_roles.insert().values(
            user_id=user.id,
            role_id=default_role.id,
        )
    )
    
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

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    data: PasswordResetRequest, 
    db: AsyncSession = Depends(get_db)
):
    
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "If this email exists, a reset link has been sent."}

    # Generate Token
    token = await create_reset_token(user.email)

    
    #  we return it so you can test it.
    print(f"DEBUG - Reset Token: {token}")
    return {
        "message": "Password reset link generated", 
        "debug_token": token 
    }

@router.post("/reset-password")
async def reset_password(
    data: PasswordResetConfirm, 
    db: AsyncSession = Depends(get_db)
):
    
    
    email = await verify_reset_token(data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid or expired reset token"
        )

   
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    user.hashed_password = hash_password(data.new_password)
    
    # unlock if locked
    user.failed_login_attempts = 0
    user.locked_until = None

    db.add(user)
    await db.commit()

    
    await delete_reset_token(data.token)

    return {"message": "Password has been updated successfully"}