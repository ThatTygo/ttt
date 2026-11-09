from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://ttt:ttt@localhost:5432/ttt"
    # Zet op False tijdens lokaal ontwikkelen over http.
    cookie_secure: bool = True
    session_days: int = 30
    timezone: str = "Europe/Amsterdam"


settings = Settings()
