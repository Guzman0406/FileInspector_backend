from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario del administrador")
    password: str = Field(..., description="Contraseña del administrador")


class LoginResponseData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
