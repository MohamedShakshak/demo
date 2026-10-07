from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str

    # Cohere (chat endpoint). Optional so /users still works without it.
    cohere_api_key: str = ""
    cohere_model: str = "command-a-03-2025"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()