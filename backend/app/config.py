from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://ttt:ttt@localhost:5432/ttt"
    # Zet op False tijdens lokaal ontwikkelen over http.
    cookie_secure: bool = True
    session_days: int = 30
    timezone: str = "Europe/Amsterdam"

    # Adres van de site, voor links in e-mails.
    site_url: str = "http://localhost:5173"
    # E-mail (SMTP). Zonder smtp_host worden er geen mails verstuurd.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    # "starttls" (poort 587), "ssl" (poort 465) of "none".
    smtp_security: str = "starttls"


settings = Settings()
