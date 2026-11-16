# Escribe el registro directo en la tabla de auditoria
# Recibe datos sueltos 
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.models import AuditLog

logger = logging.getLogger(__name__)


async def log_audit(
    db: AsyncSession,
    *,
    module: str,
    file_size_bytes: int,
    file_type: str | None,
    success: bool,
    error_code: str | None = None,
) -> None:
    try:
        registro = AuditLog(
            module=module,
            file_size_bytes=file_size_bytes,
            file_type=file_type,
            success=success,
            error_code=error_code,
        )
        db.add(registro)
        await db.commit()
    except Exception:
        logger.exception("No se pudo guardar el registro de auditoría")
        await db.rollback()
