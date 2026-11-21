import base64
import binascii

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InvalidBase64Error, FileTooLargeError
from app.core.shared import tamano_base64_estimado
from app.modules.audit.repository import log_audit
from app.modules.compare.repository import comparar_archivos
from app.modules.compare.schemas import CompareRequest


async def procesar_comparacion(db: AsyncSession, datos: CompareRequest) -> dict:
    tamano_estimado_a = tamano_base64_estimado(datos.file_base64_a)
    tamano_estimado_b = tamano_base64_estimado(datos.file_base64_b)

    if tamano_estimado_a > settings.max_size_comparator or tamano_estimado_b > settings.max_size_comparator:
        await log_audit(
            db,
            module="compare",
            file_size_bytes=max(tamano_estimado_a, tamano_estimado_b),
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("Uno de los archivos excede el tamaño máximo permitido para comparar (20MB)")

    try:
        contenido_a = base64.b64decode(datos.file_base64_a, validate=True)
        contenido_b = base64.b64decode(datos.file_base64_b, validate=True)
    except (binascii.Error, ValueError):
        await log_audit(
            db,
            module="compare",
            file_size_bytes=max(tamano_estimado_a, tamano_estimado_b),
            file_type=None,
            success=False,
            error_code="INVALID_BASE64",
        )
        raise InvalidBase64Error("Alguno de los archivos enviados no es Base64 válido")

    if len(contenido_a) > settings.max_size_comparator or len(contenido_b) > settings.max_size_comparator:
        await log_audit(
            db,
            module="compare",
            file_size_bytes=max(len(contenido_a), len(contenido_b)),
            file_type=None,
            success=False,
            error_code="FILE_TOO_LARGE",
        )
        raise FileTooLargeError("Uno de los archivos excede el tamaño máximo permitido para comparar (20MB)")

    resultado = comparar_archivos(contenido_a, contenido_b)

    await log_audit(
        db,
        module="compare",
        file_size_bytes=resultado["size_a"] + resultado["size_b"],
        file_type=None,
        success=True,
    )

    return {
        "filename_a": datos.filename_a,
        "filename_b": datos.filename_b,
        **resultado,
    }
