from pydantic import BaseModel, Field


class CleanRequest(BaseModel):
    file_base64: str = Field(..., description="Archivo codificado en Base64")
    filename: str = Field(..., description="Nombre original del archivo, incluyendo extensión")


class CleanResponseData(BaseModel):
    filename: str
    file_type: str
    original_size_bytes: int
    cleaned_size_bytes: int
    removed_metadata: list[str]
    cleaned_file_base64: str
