# app/api/routes/admin.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from app.api.dependency import RoleChecker

router = APIRouter(prefix="/admin", tags=["admin"])

admin = RoleChecker(["admin"])

@router.post("/users/{user_id}/promote", status_code=status.HTTP_200_OK, dependencies=[Depends(admin)])
async def promote_user_to_admin(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
   
    # Fetch the user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the 'admin' role
    role_result = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = role_result.scalar_one_or_none()

    if not admin_role:
        raise HTTPException(status_code=500, detail="Admin role not initialized")

    # Check if already admin
    if admin_role in user.roles:
        return {"message": "User is already an admin"}

    
    user.roles.append(admin_role)
    await db.commit()
    
    return {"message": f"User {user.email} has been promoted to admin"}