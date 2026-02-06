from app.db.base import Base
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import String, Integer

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
    )