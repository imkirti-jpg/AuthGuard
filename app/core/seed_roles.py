from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role import Role


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role import Role

async def seed_roles(db: AsyncSession) -> None:

    for role_name in ("admin", "user"):
        print("Checking role:", role_name)

        result = await db.execute(
            select(Role).where(Role.name == role_name)
        )
        role = result.scalar_one_or_none()

        if role:
            print("Already exists:", role_name)
        else:
            print("Inserting:", role_name)
            db.add(Role(name=role_name))

    await db.commit()
    
