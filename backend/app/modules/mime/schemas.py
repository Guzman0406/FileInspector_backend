from pydantic import BaseModel, Field


class MimeRequest(BaseModel):
    file_base64: str = Field(..., description="Archivo codificado en Base64")
    filename: str = Field(..., description="Nombre original del archivo, incluyendo extensión")


class MimeResponseData(BaseModel):
    filename: str
    declared_extension: str
    detected_mime_type: str
    extension_matches: bool
    suspicious: bool
    suspicious_reasons: list[str]
