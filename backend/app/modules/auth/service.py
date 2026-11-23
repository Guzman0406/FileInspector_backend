from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.modules.auth.repository import crear_admin, contar_admins, obtener_admin_por_username
from app.modules.auth.schemas import CreateAdminRequest, LoginRequest

contexto_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashear_password(password: str) -> str:
    return contexto_hash.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    return contexto_hash.verify(password, password_hash)


def crear_access_token(username: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": username, "exp": expira}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def iniciar_sesion(db: AsyncSession, datos: LoginRequest) -> dict:
    admin = await obtener_admin_por_username(db, datos.username)

    if admin is None or not verificar_password(datos.password, admin.password_hash):
        raise UnauthorizedError("Usuario o contraseña incorrectos")

    token = crear_access_token(admin.username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": settings.jwt_expire_minutes,
    }


async def obtener_admin_actual(
    authorization: str = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
   
    if authorization is None or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Falta el token de autenticación")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise UnauthorizedError("Token inválido o expirado")

    username = payload.get("sub")
    admin = await obtener_admin_por_username(db, username)
    if admin is None:
        raise UnauthorizedError("El usuario del token ya no existe")

    return admin

async def configurar_primer_admin(db: AsyncSession, datos: CreateAdminRequest, clave_setup: str) -> dict:
    if clave_setup != settings.admin_setup_key:
        raise UnauthorizedError("Clave de configuración incorrecta")

    if await contar_admins(db) > 0:
        raise UnauthorizedError("Ya existe un administrador, este endpoint ya no está disponible")

    password_hash = hashear_password(datos.password)
    await crear_admin(db, datos.username, password_hash)

    return {"username": datos.username, "mensaje": "Administrador creado correctamente"}