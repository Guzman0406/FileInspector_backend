from pydantic import BaseModel, Field

# Describir lo que se manda 
class ExifRequest(BaseModel):
    file_base64: str = Field(..., description="Archivo codificado en Base64")
    filename: str = Field(..., description="Nombre original del archivo, incluyendo extensión")


class ExifField(BaseModel):
    tag: str
    value: str
    sensitive: bool


class GpsData(BaseModel):
    latitude: float
    longitude: float


class ExifData(BaseModel):
    fields: list[ExifField]
    gps: GpsData | None = None
    has_sensitive_data: bool


class ExifResponseData(BaseModel):
    filename: str
    file_type: str
    exif: ExifData
