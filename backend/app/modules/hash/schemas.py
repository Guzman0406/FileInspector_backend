from pydantic import BaseModel, Field


class HashRequest(BaseModel):
    file_base64: str = Field(..., description="Archivo codificado en Base64")
    filename: str = Field(..., description="Nombre original del archivo, incluyendo extensión")


class HashValues(BaseModel):
    md5: str
    sha1: str
    sha256: str
    sha512: str


class HashResponseData(BaseModel):
    filename: str
    file_size_bytes: int
    hashes: HashValues
    weak_algorithms_warning: str
