from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.responses import success_response
from app.modules.auth.schemas import CreateAdminRequest, LoginRequest
from app.modules.auth.service import configurar_primer_admin, iniciar_sesion

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=None)
@limiter.limit("10/minute")
async def login(
    request: Request,
    datos: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    resultado = await iniciar_sesion(db, datos)
    return success_response(data=resultado)


@router.post("/setup-admin", response_model=None)
@limiter.limit("5/minute")
async def setup_admin(
    request: Request,
    datos: CreateAdminRequest,
    x_setup_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    resultado = await configurar_primer_admin(db, datos, x_setup_key)
    return success_response(data=resultado)