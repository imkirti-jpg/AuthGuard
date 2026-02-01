import secrets
from datetime import timedelta
from app.db.redis import redis_client
from app.core.config import get_settings
from uuid import UUID
import uuid

settings = get_settings()


async def create_refresh_token(user_id: uuid.UUID) -> str:
    
    token = str(uuid.uuid4())
    # Use the token as the key to store the user_id
    key = f"refresh_token:{token}"

    print("CREATED TOKEN:", token)


    await redis_client.set(
        key,
        str(user_id),
        ex=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return token



async def validate_and_rotate_refresh_token(token: str) -> tuple[str, str]:
    key = f"refresh_token:{token}"
    
    # Check if token exists in Redis
    user_id = await redis_client.get(key)
    if not user_id:
        raise ValueError("Invalid or expired refresh token")
    
    if isinstance(user_id, bytes):
        user_id = user_id.decode("utf-8")
 

    # (delete) the old token immediately
    await redis_client.delete(key)

    # Issue a brand new token for rotation
    new_token = await create_refresh_token(uuid.UUID(user_id))

    print("RECEIVED TOKEN:", token)
    print("REDIS KEY:", key)

    
    return user_id, new_token




async def revoke_refresh_token(token: str) -> bool:
    key = f"refresh_token:{token}"
    result = await redis_client.delete(key)
    return result > 0