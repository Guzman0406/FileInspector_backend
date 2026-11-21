from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog


async def contar_peticiones_por_modulo(db: AsyncSession) -> dict[str, int]:
    stmt = (
        select(AuditLog.module, func.count())
        .where(AuditLog.deleted_at.is_(None))
        .group_by(AuditLog.module)
    )
    filas = (await db.execute(stmt)).all()
    return {modulo: total for modulo, total in filas}


async def contar_tasa_exito_por_modulo(db: AsyncSession) -> dict[str, tuple[int, int]]:
    """Regresa {modulo: (total_requests, successful_requests)} por cada módulo con datos."""
    stmt = (
        select(
            AuditLog.module,
            func.count(),
            func.sum(case((AuditLog.success.is_(True), 1), else_=0)),
        )
        .where(AuditLog.deleted_at.is_(None))
        .group_by(AuditLog.module)
    )
    filas = (await db.execute(stmt)).all()
    return {modulo: (total, exitosos or 0) for modulo, total, exitosos in filas}


async def contar_errores_comunes(db: AsyncSession) -> list[tuple[str, int]]:
    stmt = (
        select(AuditLog.error_code, func.count())
        .where(
            AuditLog.deleted_at.is_(None),
            AuditLog.success.is_(False),
            AuditLog.error_code.is_not(None),
        )
        .group_by(AuditLog.error_code)
        .order_by(func.count().desc())
    )
    return (await db.execute(stmt)).all()


async def calcular_tamano_promedio_por_modulo(db: AsyncSession) -> dict[str, tuple[int, float, int]]:
    """Regresa {modulo: (total_requests, promedio_bytes, suma_bytes)}, solo con peticiones exitosas."""
    stmt = (
        select(
            AuditLog.module,
            func.count(),
            func.avg(AuditLog.file_size_bytes),
            func.sum(AuditLog.file_size_bytes),
        )
        .where(AuditLog.deleted_at.is_(None), AuditLog.success.is_(True))
        .group_by(AuditLog.module)
    )
    filas = (await db.execute(stmt)).all()
    return {
        modulo: (total, float(promedio), int(suma))
        for modulo, total, promedio, suma in filas
    }
