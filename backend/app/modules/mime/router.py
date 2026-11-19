from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.responses import success_response
from app.modules.mime.schemas import MimeRequest
from app.modules.mime.service import procesar_mime

router = APIRouter(prefix="/api/v1", tags=["Mime"])


@router.post("/mime", response_model=None)
@limiter.limit("30/minute")
async def detectar_mime_endpoint(
    request: Request,
    datos: MimeRequest,
    db: AsyncSession = Depends(get_db),
):
    resultado = await procesar_mime(db, datos)
    return success_response(data=resultado)
