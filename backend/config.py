"""
FarmSphere AI — Application Configuration
Reads all settings from environment variables with sensible defaults.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────
    app_name: str = "FarmSphere AI"
    app_env: str = Field(default="development", env="APP_ENV")
    app_secret_key: str = Field(default="dev-secret-key", env="APP_SECRET_KEY")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cors_origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")

    # ── Google / Gemini ───────────────────────────────────────
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    gemini_model: str = "gemini-2.0-flash"
    gemini_model_fallback: str = "gemini-1.5-flash"  # used when primary hits rate limits
    gemini_vision_model: str = "gemini-2.0-flash"
    embedding_model: str = "models/text-embedding-004"

    # ── Weather ───────────────────────────────────────────────
    openweather_api_key: str = Field(default="", env="OPENWEATHER_API_KEY")
    default_lat: float = Field(default=28.6139, env="DEFAULT_LAT")
    default_lon: float = Field(default=77.2090, env="DEFAULT_LON")

    # ── Search ────────────────────────────────────────────────
    tavily_api_key: str = Field(default="", env="TAVILY_API_KEY")

    # ── PostgreSQL ────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql://farmsphere:farmsphere_secret@localhost:5432/farmsphere_db",
        env="DATABASE_URL",
    )

    # ── ChromaDB ──────────────────────────────────────────────
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8001, env="CHROMA_PORT")

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # ── Google Earth Engine ───────────────────────────────────
    gee_mode: str = Field(default="mock", env="GEE_MODE")
    gee_service_account: str = Field(default="", env="GEE_SERVICE_ACCOUNT")
    gee_key_file: str = Field(default="gee-key.json", env="GEE_KEY_FILE")

    # ── Agent Thresholds ──────────────────────────────────────
    disease_confidence_threshold: float = 0.75
    hitl_enabled: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = (".env", "../.env")
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
