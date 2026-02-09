from app.core.refresh import validate_and_rotate_refresh_token
from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.refresh import RefreshRequest, TokenResponse
from fastapi import APIRouter, HTTPException, status

settings = get_settings()

router = APIRouter()
from fastapi import APIRouter, HTTPException, status
from app.core.refresh import validate_and_rotate_refresh_token 
from app.core.security import create_access_token
from app.schemas.refresh import RefreshRequest

router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest):
    try:
        # Pass the token string from the request body
        user_id, new_refresh_token = await validate_and_rotate_refresh_token(data.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    # Issue new access token using the user_id recovered from Redis
    new_access_token = create_access_token(subject=str(user_id))

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES ,
    }
