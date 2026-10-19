from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://lorenzini:lorenzini@localhost:5432/lorenzini_track"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
