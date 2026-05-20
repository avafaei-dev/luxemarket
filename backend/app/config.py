from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://luxe:luxe_dev@localhost:5432/luxemarket"
    redis_url: str = "redis://localhost:6379"
    app_env: str = "development"
    secret_key: str = "change_me_in_production"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()