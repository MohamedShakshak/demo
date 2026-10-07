from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str

    # Cohere (chat endpoint). Optional so /users still works without it.
    cohere_api_key: str = ""
    cohere_model: str = "command-a-03-2025"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        # Tolerate stray whitespace/quotes pasted into the Railway dashboard.
        v = v.strip().strip('"').strip("'").strip()
        if not v:
            raise ValueError(
                "DATABASE_URL is empty. On Railway, set it to ${{<PostgresServiceName>.DATABASE_URL}} "
                "and make sure the service name matches exactly."
            )
        if v.startswith("${{"):
            raise ValueError(f"DATABASE_URL reference was not resolved by Railway: {v}")

        # Railway gives postgresql:// (sometimes postgres://); asyncpg needs postgresql+asyncpg://
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                return "postgresql+asyncpg://" + v[len(prefix):]
        if v.startswith("postgresql+asyncpg://"):
            return v

        scheme = v.split("://", 1)[0] if "://" in v else v[:15] + "..."
        raise ValueError(f"DATABASE_URL must start with postgresql://, got: {scheme!r}")

settings = Settings()