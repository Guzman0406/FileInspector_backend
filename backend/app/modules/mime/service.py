import asyncio
import base64
import binascii
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, InvalidBase64Error, ProcessingTimeoutError
from app.core.shared import tamano_base64_estimado
from app.modules.audit.repository import log_audit
from app.modules.mime.repository import detectar_mime
from app.modules.mime.schemas import MimeRequest

logger = logging.getLogger(__name__)


async def procesar_mime(db: AsyncSession, datos: MimeRequest) -> dict:
    tamano_estimado = tamano_base64_estimado(datos.file_base64)

    if tamano_estimado > settings.max_size_mime:
        await log_audit(
            db,
            module="mime",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para mime (10MB)")

    try:
        contenido = base64.b64decode(datos.file_base64, validate=True)
    except (binascii.Error, ValueError):
        await log_audit(
            db,
            module="mime",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="INVALID_BASE64",
        )
        raise InvalidBase64Error("El archivo enviado no es Base64 válido")

    if len(contenido) > settings.max_size_mime:
        await log_audit(
            db,
            module="mime",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para mime (10MB)")

    try:
        resultado = await asyncio.wait_for(
            asyncio.to_thread(detectar_mime, contenido, datos.filename),
            timeout=30,
        )
    except asyncio.TimeoutError:
        await log_audit(
            db,
            module="mime",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="PROCESSING_TIMEOUT",
        )
        raise ProcessingTimeoutError("El procesamiento del archivo tardó demasiado")

    await log_audit(
        db,
        module="mime",
        file_size_bytes=len(contenido),
        file_type=resultado["detected_mime_type"],
        success=True,
    )

    return {
        "filename": datos.filename,
        **resultado,
    }
