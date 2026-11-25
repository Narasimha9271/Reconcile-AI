from functools import lru_cache
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RECONCILEAI_")
    environment: str = Field(default="development", pattern="^(development|test|staging|production)$")
    service_name: str = "reconcileai-api"
    version: str = "0.1.0"
    database_url: str = Field(default="postgresql+psycopg://reconcileai:reconcileai_dev_only@localhost:5432/reconcileai", validation_alias=AliasChoices("DATABASE_URL", "RECONCILEAI_DATABASE_URL"))
    document_storage_path: str = "./var/documents"
    session_secret: str = Field(default="local-development-secret-change-before-production", validation_alias=AliasChoices("SESSION_SECRET", "RECONCILEAI_SESSION_SECRET"))
    google_client_id: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "RECONCILEAI_GOOGLE_CLIENT_ID"))
    google_client_secret: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "RECONCILEAI_GOOGLE_CLIENT_SECRET"))
    google_callback_url: str = Field(default="http://localhost:4000/api/auth/google/callback", validation_alias=AliasChoices("GOOGLE_CALLBACK_URL", "RECONCILEAI_GOOGLE_CALLBACK_URL"))
    google_allowed_email: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_ALLOWED_EMAIL", "RECONCILEAI_GOOGLE_ALLOWED_EMAIL"))
    google_finance_approver_emails: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_FINANCE_APPROVER_EMAILS", "RECONCILEAI_GOOGLE_FINANCE_APPROVER_EMAILS"))
    frontend_url: str = Field(default="http://localhost:3000", validation_alias=AliasChoices("FRONTEND_URL", "RECONCILEAI_FRONTEND_URL"))
    cors_allowed_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000", validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS", "RECONCILEAI_CORS_ALLOWED_ORIGINS"))
    openai_api_key: str | None = Field(default=None, validation_alias=AliasChoices("OPENAI_API_KEY", "RECONCILEAI_OPENAI_API_KEY"))
    openai_model: str = Field(default="gpt-4o-mini", validation_alias=AliasChoices("OPENAI_MODEL", "RECONCILEAI_OPENAI_MODEL"))

    @field_validator("database_url")
    @classmethod
    def use_psycopg(cls, url: str) -> str:
        return url.replace("postgresql://", "postgresql+psycopg://", 1) if url.startswith("postgresql://") else url

@lru_cache
def get_settings() -> Settings:
    return Settings()
