from datetime import datetime
import uuid
from sqlalchemy.orm import mapped_column, Mapped , relationship
from sqlalchemy import String, Integer, func
from app.db.base import Base
from sqlalchemy import DateTime



class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        server_default=func.now(),
        nullable=False  )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        server_default=func.now(),  
        onupdate=func.now(),
        nullable=False  )
    
    roles = relationship(
        "Role",     
        secondary="user_roles",
        back_populates="users",
        lazy="selectin"
    )
    
    