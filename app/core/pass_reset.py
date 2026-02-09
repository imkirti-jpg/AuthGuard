import uuid
from app.db.redis import redis_client
from app.core.config import get_settings

settings = get_settings()

async def create_reset_token(email: str) -> str:
    token = str(uuid.uuid4())
    key = f"reset_password:{token}"
    
    await redis_client.set(
        key, 
        email, 
        ex=settings.RESET_TOKEN_EXPIRE_MINUTES * 60
    )
    return token

async def verify_reset_token(token: str) -> str | None:
    key = f"reset_password:{token}"
    email = await redis_client.get(key)
    
    if not email:
        return None
        
    # Redis might return bytes, so decode if necessary
    return email if isinstance(email, str) else email.decode("utf-8")

async def delete_reset_token(token: str):
    """Invalidate the token after use."""
    key = f"reset_password:{token}"
    await redis_client.delete(key)