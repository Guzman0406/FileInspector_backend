import asyncio
import base64
import binascii
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.shared import tamano_base64_estimado
from app.core.exceptions import (
    FileTooLargeError,
    InvalidBase64Error,
    ProcessingTimeoutError,
    UnsupportedFormatError,
)
from app.modules.audit.repository import log_audit
from app.modules.exif.repository import extraer_exif
from app.modules.exif.schemas import ExifRequest

logger = logging.getLogger(__name__)

FORMATOS_SOPORTADOS = {"image/jpeg", "image/png", "image/tiff", "image/heic", "image/heif"}


async def procesar_exif(db: AsyncSession, datos: ExifRequest) -> dict:
    tamano_estimado = tamano_base64_estimado(datos.file_base64)

# El arvchivo es mas grande de lo compatible 
# Sino es compatible se guarda en la auditoria
    if tamano_estimado > settings.max_size_exif:
        await log_audit(
            db,
            module="exif",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para EXIF (10MB)")

# Convierte Base64 a bytes para saber si trae datos invalidos
    try:
        contenido = base64.b64decode(datos.file_base64, validate=True)
    except (binascii.Error, ValueError):
        await log_audit(
            db,
            module="exif",
            file_size_bytes=tamano_estimado,
            file_type=None,
            success=False,
            error_code="INVALID_BASE64",
        )
        raise InvalidBase64Error("El archivo enviado no es Base64 válido")

# Segunda validacion de tamaño pero con bytes reales
# (Sin la inflacion de los bytes)
    if len(contenido) > settings.max_size_exif:
        await log_audit(
            db,
            module="exif",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("El archivo excede el tamaño máximo permitido para EXIF (10MB)")

# Se ejecuta la extraccion del exif y se da una espera de 30 segundos o error
    try:
        resultado = await asyncio.wait_for(
            asyncio.to_thread(extraer_exif, contenido),
            timeout=30,
        )
    except asyncio.TimeoutError:
        await log_audit(
            db,
            module="exif",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="PROCESSING_TIMEOUT",
        )
        raise ProcessingTimeoutError("El procesamiento del archivo tardó demasiado")
    except Exception:
        logger.exception("Error inesperado procesando EXIF")
        await log_audit(
            db,
            module="exif",
            file_size_bytes=len(contenido),
            file_type=None,
            success=False,
            error_code="UNSUPPORTED_FORMAT",
        )
        raise UnsupportedFormatError("No se pudo leer el archivo. Verifica que sea JPEG, PNG, TIFF o HEIC/HEIF")

# Formato no valido 
    if resultado["file_type"] not in FORMATOS_SOPORTADOS:
        await log_audit(
            db,
            module="exif",
            file_size_bytes=len(contenido),
            file_type=resultado["file_type"],
            success=False,
            error_code="UNSUPPORTED_FORMAT",
        )
        raise UnsupportedFormatError("Formato de archivo no soportado para EXIF")

    await log_audit(
        db,
        module="exif",
        file_size_bytes=len(contenido),
        file_type=resultado["file_type"],
        success=True,
    )

    return {
        "filename": datos.filename,
        "file_type": resultado["file_type"],
        "exif": {
            "fields": resultado["fields"],
            "gps": resultado["gps"],
            "has_sensitive_data": resultado["has_sensitive_data"],
        },
    }
