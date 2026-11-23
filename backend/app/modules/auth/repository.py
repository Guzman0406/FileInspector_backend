from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import AdminUser


async def obtener_admin_por_username(db: AsyncSession, username: str) -> AdminUser | None:
    stmt = select(AdminUser).where(
        AdminUser.username == username,
        AdminUser.deleted_at.is_(None),
    )
    resultado = await db.execute(stmt)
    return resultado.scalar_one_or_none()


async def contar_admins(db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(AdminUser).where(AdminUser.deleted_at.is_(None))
    resultado = await db.execute(stmt)
    return resultado.scalar_one()


async def crear_admin(db: AsyncSession, username: str, password_hash: str) -> AdminUser:
    admin = AdminUser(username=username, password_hash=password_hash)
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin
