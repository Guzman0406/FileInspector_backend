from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import AdminUser


async def obtener_admin_por_username(db: AsyncSession, username: str) -> AdminUser | None:
    stmt = select(AdminUser).where(
        AdminUser.username == username,
        AdminUser.deleted_at.is_(None),
    )
    resultado = await db.execute(stmt)
    return resultado.scalar_one_or_none()
