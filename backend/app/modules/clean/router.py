from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.responses import success_response
from app.modules.clean.schemas import CleanRequest
from app.modules.clean.service import procesar_clean

router = APIRouter(prefix="/api/v1", tags=["Clean"])


@router.post("/clean", response_model=None)
@limiter.limit("30/minute")
async def limpiar(
    request: Request,
    datos: CleanRequest,
    db: AsyncSession = Depends(get_db),
):
    resultado = await procesar_clean(db, datos)
    return success_response(data=resultado)
