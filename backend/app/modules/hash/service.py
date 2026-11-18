import asyncio
import base64
import binascii
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, InvalidBase64Error, ProcessingTimeoutError
from app.core.shared import tamano_base64_estimado
from app.modules.audit.repository import log_audit
from app.modules.hash.repository import calcular_hashes
from app.modules.hash.schemas import HashRequest

logger = logging.getLogger(__name__)

MENSAJE_ALGORITMOS_DEBILES = (
    "MD5 y SHA-1 ya no se consideran criptográficamente seguros; "
    "usa SHA-256 o SHA-512 para verificación de integridad."
)


async def procesar_hash(db: AsyncSession, datos: HashRequest) -> dict:
    tamano_estimado = tamano_base64_estimado(datos.file_base64)

    if tamano_estimado > settings.max_size_hash:
        await log_audit(
            db,
            module="hash",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para hash (50MB)")

    try:
        contenido = base64.b64decode(datos.file_base64, validate=True)
    except (binascii.Error, ValueError):
        await log_audit(
            db,
            module="hash",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="INVALID_BASE64",
        )
        raise InvalidBase64Error("El archivo enviado no es Base64 válido")

    if len(contenido) > settings.max_size_hash:
        await log_audit(
            db,
            module="hash",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para hash (50MB)")

    try:
        hashes = await asyncio.wait_for(
            asyncio.to_thread(calcular_hashes, contenido),
            timeout=30,
        )
    except asyncio.TimeoutError:
        await log_audit(
            db,
            module="hash",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="PROCESSING_TIMEOUT",
        )
        raise ProcessingTimeoutError("El procesamiento del archivo tardó demasiado")

    await log_audit(
        db,
        module="hash",
        file_size_bytes=len(contenido),
        file_type=None,
        success=True,
    )

    return {
        "filename": datos.filename,
        "file_size_bytes": len(contenido),
        "hashes": hashes,
        "weak_algorithms_warning": MENSAJE_ALGORITMOS_DEBILES,
    }
