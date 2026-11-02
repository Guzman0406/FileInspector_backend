from fastapi import FastAPI

from app.core.error_handlers import register_error_handlers

app = FastAPI(
    title="FileInspector API",
    description="API pública para inspección y limpieza de metadatos de archivos.",
    version="0.1.0",
)

register_error_handlers(app)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
