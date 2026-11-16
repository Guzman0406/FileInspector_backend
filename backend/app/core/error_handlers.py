from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded

from app.core.exceptions import AppError
from app.core.responses import error_response


async def app_error_handler(request: Request, exc: AppError):
    return error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return error_response(
        code="VALIDATION_ERROR",
        message="Los datos enviados no son válidos",
        status_code=422,
        details=details,
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return error_response(
        code="RATE_LIMITED",
        message="Has hecho demasiadas peticiones. Espere un momento e intente nuevamente",
        status_code=429,
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    return error_response(
        code="INTERNAL_ERROR",
        message="Ocurrió un error inesperado en el servidor",
        status_code=500,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
