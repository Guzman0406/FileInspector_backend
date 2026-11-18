from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.responses import success_response
from app.modules.hash.schemas import HashRequest
from app.modules.hash.service import procesar_hash

router = APIRouter(prefix="/api/v1", tags=["Hash"])


@router.post("/hash", response_model=None)
@limiter.limit("30/minute")
async def calcular_hash(
    request: Request,
    datos: HashRequest,
    db: AsyncSession = Depends(get_db),
):
    resultado = await procesar_hash(db, datos)
    return success_response(data=resultado)
