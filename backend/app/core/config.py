from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://poseidon:poseidon@localhost:5432/poseidon"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
