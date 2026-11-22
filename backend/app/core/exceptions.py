class AppError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, details: list | None = None):
        self.message = message
        self.details = details or []
        super().__init__(message)


class InvalidBase64Error(AppError):
    status_code = 400
    code = "INVALID_BASE64"


class FileTooLargeError(AppError):
    status_code = 413
    code = "FILE_TOO_LARGE"


class UnsupportedFormatError(AppError):
    status_code = 415
    code = "UNSUPPORTED_FORMAT"


class ProcessingTimeoutError(AppError):
    status_code = 504
    code = "PROCESSING_TIMEOUT"


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"

