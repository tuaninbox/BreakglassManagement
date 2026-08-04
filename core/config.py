from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Breakglass"
    debug: bool = True

    database_url: str = "sqlite+aiosqlite:///./breakglass.db"
    # later: "postgresql+asyncpg://user:pass@host/db"

    vault_addr: str = "http://localhost:8200"
    vault_token: str = "changeme"

    smtp_host: str = "localhost"
    smtp_port: int = 25
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str = "breakglass@example.com"

    jwt_secret: str = "super-secret"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    # Nagios XI / Core API
    nagios_url: str = "https://nagios.example.com"
    nagios_api_token: str | None = None  # or username/password if you prefer
    nagios_verify_ssl: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
