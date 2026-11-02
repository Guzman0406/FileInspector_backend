from typing import Any

from fastapi.responses import JSONResponse


def success_response(data: Any = None, meta: dict | None = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "meta": meta or {},
        },
    )


def error_response(code: str, message: str, status_code: int, details: list | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            },
        },
    )
