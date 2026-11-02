from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = False

    database_url: str 

    max_size_exif: int = 10 * 1024 * 1024
    max_size_cleaner: int = 10 * 1024 * 1024
    max_size_hash: int = 50 * 1024 * 1024
    max_size_comparator: int = 20 * 1024 * 1024

    rate_limit_default: str = "30/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
