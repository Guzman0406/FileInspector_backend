import asyncio
import base64
import binascii
import io
import logging

from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    FileTooLargeError,
    InvalidBase64Error,
    ProcessingTimeoutError,
    UnsupportedFormatError,
)
from app.core.shared import tamano_base64_estimado
from app.modules.audit.repository import log_audit
from app.modules.clean.repository import limpiar_metadatos
from app.modules.clean.schemas import CleanRequest

logger = logging.getLogger(__name__)

FORMATOS_SOPORTADOS = {"image/jpeg", "image/png"}


def _detectar_file_type(contenido: bytes) -> str:
    imagen = Image.open(io.BytesIO(contenido))
    imagen.load()
    formato = imagen.format
    return "image/jpeg" if formato == "MPO" else f"image/{formato.lower()}"


async def procesar_clean(db: AsyncSession, datos: CleanRequest) -> dict:
    tamano_estimado = tamano_base64_estimado(datos.file_base64)

    if tamano_estimado > settings.max_size_cleaner:
        await log_audit(
            db,
            module="clean",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para clean (10MB)")

    try:
        contenido = base64.b64decode(datos.file_base64, validate=True)
    except (binascii.Error, ValueError):
        await log_audit(
            db,
            module="clean",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="INVALID_BASE64",
        )
        raise InvalidBase64Error("El archivo enviado no es Base64 válido")

    if len(contenido) > settings.max_size_cleaner:
        await log_audit(
            db,
            module="clean",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para clean (10MB)")

    try:
        file_type = await asyncio.wait_for(
            asyncio.to_thread(_detectar_file_type, contenido),
            timeout=30,
        )
    except asyncio.TimeoutError:
        await log_audit(
            db,
            module="clean",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="PROCESSING_TIMEOUT",
        )
        raise ProcessingTimeoutError("El procesamiento del archivo tardó demasiado")
    except Exception:
        logger.exception("Error inesperado detectando el tipo de archivo en clean")
        await log_audit(
            db,
            module="clean",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="UNSUPPORTED_FORMAT",
        )
        raise UnsupportedFormatError("No se pudo leer el archivo. Verifica que sea una imagen válida")

    if file_type not in FORMATOS_SOPORTADOS:
        await log_audit(
            db,
            module="clean",
            file_size_bytes=len(contenido),
            file_type=file_type,
            success=False,
            error_code="UNSUPPORTED_FORMAT",
        )
        raise UnsupportedFormatError("Clean solo soporta JPEG y PNG")

    try:
        contenido_limpio, eliminados = await asyncio.wait_for(
            asyncio.to_thread(limpiar_metadatos, contenido, file_type),
            timeout=30,
        )
    except asyncio.TimeoutError:
        await log_audit(
            db,
            module="clean",
            file_size_bytes=len(contenido),
            file_type=file_type,
            success=False,
            error_code="PROCESSING_TIMEOUT",
        )
        raise ProcessingTimeoutError("El procesamiento del archivo tardó demasiado")

    await log_audit(
        db,
        module="clean",
        file_size_bytes=len(contenido),
        file_type=file_type,
        success=True,
    )

    return {
        "filename": datos.filename,
        "file_type": file_type,
        "original_size_bytes": len(contenido),
        "cleaned_size_bytes": len(contenido_limpio),
        "removed_metadata": eliminados,
        "cleaned_file_base64": base64.b64encode(contenido_limpio).decode("ascii"),
    }
