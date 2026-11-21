from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    file_base64_a: str = Field(..., description="Primer archivo codificado en Base64")
    filename_a: str = Field(..., description="Nombre del primer archivo")
    file_base64_b: str = Field(..., description="Segundo archivo codificado en Base64")
    filename_b: str = Field(..., description="Nombre del segundo archivo")


class ByteDifference(BaseModel):
    position: int
    value_a: int | None
    value_b: int | None


class CompareResponseData(BaseModel):
    filename_a: str
    filename_b: str
    size_a: int
    size_b: int
    identical: bool
    total_differences: int
    truncated: bool
    differences: list[ByteDifference]
