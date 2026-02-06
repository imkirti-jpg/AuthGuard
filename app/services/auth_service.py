from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.exceptions import AccountLocked, InvalidCredentials

settings = get_settings()


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    email = email.lower().strip()

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    # User not found
    if not user:
        raise InvalidCredentials()

    # Account locked
    if user.locked_until and user.locked_until > now:
        raise AccountLocked()

    #  Wrong password
    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = now + timedelta(
                minutes=settings.LOCKOUT_MINUTES
            )

        await db.commit()
        raise InvalidCredentials()

    #  Success
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()

    return user