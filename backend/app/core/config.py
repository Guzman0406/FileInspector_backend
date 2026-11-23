# Definimos el tamaño de archivos soportados 
# para no saturar las cargas
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = False

    database_url: str #sino hay base truena

    # tamaño en byetes
    max_size_exif: int = 10 * 1024 * 1024
    max_size_mime: int = 10 * 1024 * 1024
    max_size_cleaner: int = 10 * 1024 * 1024
    max_size_hash: int = 50 * 1024 * 1024
    max_size_comparator: int = 20 * 1024 * 1024

    # usado para las diferencias en el modulo compare
    compare_diff_limit: int = 20

    rate_limit_default: str = "30/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    
    admin_setup_key: str

settings = Settings()
