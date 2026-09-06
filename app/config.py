from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATA_DIR: str = "data"

    # Optional real AI providers (any OpenAI-compatible vision endpoint)
    AI_BASE_URL: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = ""

    # Optional video provider
    REPLICATE_API_TOKEN: str = ""
    VIDEO_MODEL: str = "prunaai/p-video"

    # Optional Supabase persistence
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
