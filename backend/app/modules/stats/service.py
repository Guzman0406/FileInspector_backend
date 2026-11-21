from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.stats.repository import (
    calcular_tamano_promedio_por_modulo,
    contar_errores_comunes,
    contar_peticiones_por_modulo,
    contar_tasa_exito_por_modulo,
)

MODULOS_VALIDOS = ["exif", "clean", "mime", "hash", "compare"]


def _porcentaje(parte: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(parte / total * 100, 1)


async def obtener_peticiones_por_modulo(db: AsyncSession) -> dict:
    conteos = await contar_peticiones_por_modulo(db)

    modules = [
        {"module": modulo, "total_requests": conteos.get(modulo, 0)}
        for modulo in MODULOS_VALIDOS
    ]

    return {
        "modules": modules,
        "total_requests": sum(item["total_requests"] for item in modules),
    }


async def obtener_tasa_exito(db: AsyncSession) -> dict:
    datos_por_modulo = await contar_tasa_exito_por_modulo(db)

    by_module = []
    total_requests = 0
    successful_requests = 0

    for modulo in MODULOS_VALIDOS:
        total, exitosos = datos_por_modulo.get(modulo, (0, 0))
        fallidos = total - exitosos

        by_module.append({
            "module": modulo,
            "total_requests": total,
            "successful_requests": exitosos,
            "failed_requests": fallidos,
            "success_rate": _porcentaje(exitosos, total),
        })

        total_requests += total
        successful_requests += exitosos

    failed_requests = total_requests - successful_requests

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": _porcentaje(successful_requests, total_requests),
        "by_module": by_module,
    }


async def obtener_errores_comunes(db: AsyncSession) -> dict:
    filas = await contar_errores_comunes(db)
    total_errors = sum(cantidad for _, cantidad in filas)

    errors = [
        {
            "error_code": codigo,
            "count": cantidad,
            "percentage": _porcentaje(cantidad, total_errors),
        }
        for codigo, cantidad in filas
    ]

    return {
        "total_errors": total_errors,
        "errors": errors,
    }


async def obtener_tamano_promedio_por_modulo(db: AsyncSession) -> dict:
    datos_por_modulo = await calcular_tamano_promedio_por_modulo(db)

    modules = []
    for modulo in MODULOS_VALIDOS:
        total, promedio_bytes, suma_bytes = datos_por_modulo.get(modulo, (0, 0.0, 0))

        modules.append({
            "module": modulo,
            "total_requests": total,
            "average_size_bytes": round(promedio_bytes),
            "average_size_mb": round(promedio_bytes / (1024 * 1024), 2),
            "total_size_bytes": suma_bytes,
        })

    return {"modules": modules}
