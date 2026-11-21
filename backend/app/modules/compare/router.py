from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.responses import success_response
from app.modules.compare.schemas import CompareRequest
from app.modules.compare.service import procesar_comparacion

router = APIRouter(prefix="/api/v1", tags=["Compare"])


@router.post("/compare", response_model=None)
@limiter.limit("30/minute")
async def comparar(
    request: Request,
    datos: CompareRequest,
    db: AsyncSession = Depends(get_db),
):
    resultado = await procesar_comparacion(db, datos)
    return success_response(data=resultado)
