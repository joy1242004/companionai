from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "CompanionAI"
    secret_key: str = Field("super-secret-key-change-me", env="COMPANIONAI_SECRET_KEY")
    access_token_expire_minutes: int = 60 * 12
    database_url: str = Field("sqlite+aiosqlite:///./companionai.db", env="COMPANIONAI_DATABASE_URL")
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5500"])

    class Config:
        env_file = ".env"


settings = Settings()
