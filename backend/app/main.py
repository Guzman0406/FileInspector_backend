from contextlib import asynccontextmanager

from fastapi import FastAPI
from PIL import Image

from app.core.database import Base, engine
from app.core.error_handlers import register_error_handlers
from app.core.limiter import limiter
from app.modules.audit.models import AuditLog  # noqa: F401 
from app.modules.exif.router import router as exif_router
from app.modules.hash.router import router as hash_router
from app.modules.mime.router import router as mime_router


# Limite de pixeles para evitar "bombas de imagen" 
Image.MAX_IMAGE_PIXELS = 50_000_000


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="FileInspector API",
    description="API pública para inspección y limpieza de metadatos en archivos.",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
register_error_handlers(app)
app.include_router(exif_router)
app.include_router(hash_router)
app.include_router(mime_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
