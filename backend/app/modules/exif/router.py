from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.responses import success_response
from app.modules.exif.schemas import ExifRequest, ExifResponseData
from app.modules.exif.service import procesar_exif

router = APIRouter(prefix="/api/v1", tags=["EXIF"])


@router.post("/exif", response_model=None)
@limiter.limit("30/minute")
async def leer_exif(
    request: Request,
    datos: ExifRequest,
    db: AsyncSession = Depends(get_db),
):
    resultado = await procesar_exif(db, datos)
    return success_response(data=resultado)
