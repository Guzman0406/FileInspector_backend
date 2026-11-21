from pydantic import BaseModel

MODULOS_VALIDOS = ["exif", "clean", "mime", "hash", "compare"]


class RequestsByModuleItem(BaseModel):
    module: str
    total_requests: int


class RequestsByModuleData(BaseModel):
    modules: list[RequestsByModuleItem]
    total_requests: int


class SuccessRateByModuleItem(BaseModel):
    module: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float


class SuccessRateData(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    by_module: list[SuccessRateByModuleItem]


class CommonErrorItem(BaseModel):
    error_code: str
    count: int
    percentage: float


class CommonErrorsData(BaseModel):
    total_errors: int
    errors: list[CommonErrorItem]


class AverageSizeByModuleItem(BaseModel):
    module: str
    total_requests: int
    average_size_bytes: int
    average_size_mb: float
    total_size_bytes: int


class AverageSizeByModuleData(BaseModel):
    modules: list[AverageSizeByModuleItem]
