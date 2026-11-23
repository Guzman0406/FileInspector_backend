import re
from pydantic import BaseModel, Field, field_validator

PATRON_USERNAME = re.compile(r"^[a-zA-Z0-9_.-]+$")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario del administrador")
    password: str = Field(..., description="Contraseña del administrador")


class LoginResponseData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class CreateAdminRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario del nuevo administrador")
    password: str = Field(..., min_length=8, description="Contraseña del nuevo administrador")

    @field_validator("username")
    @classmethod
    def username_sin_emojis_ni_simbolos_raros(cls, valor: str) -> str:
        if not PATRON_USERNAME.match(valor):
            raise ValueError("El usuario solo puede contener letras, números, puntos, guiones y guion bajo")
        return valor
