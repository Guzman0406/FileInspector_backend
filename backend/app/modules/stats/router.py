from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.responses import success_response
from app.modules.auth.service import obtener_admin_actual
from app.modules.stats.service import (
    obtener_errores_comunes,
    obtener_peticiones_por_modulo,
    obtener_tamano_promedio_por_modulo,
    obtener_tasa_exito,
)

router = APIRouter(
    prefix="/api/v1/stats",
    tags=["Stats"],
    dependencies=[Depends(obtener_admin_actual)],
)


@router.get("/requests-by-module", response_model=None)
@limiter.limit("30/minute")
async def requests_by_module(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    resultado = await obtener_peticiones_por_modulo(db)
    return success_response(data=resultado)


@router.get("/success-rate", response_model=None)
@limiter.limit("30/minute")
async def success_rate(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    resultado = await obtener_tasa_exito(db)
    return success_response(data=resultado)


@router.get("/common-errors", response_model=None)
@limiter.limit("30/minute")
async def common_errors(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    resultado = await obtener_errores_comunes(db)
    return success_response(data=resultado)


@router.get("/average-size-by-module", response_model=None)
@limiter.limit("30/minute")
async def average_size_by_module(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    resultado = await obtener_tamano_promedio_por_modulo(db)
    return success_response(data=resultado)
