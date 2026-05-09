from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    secret_key: str
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"

    github_client_id: str = ""
    github_client_secret: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""


# pydantic-settings populates fields from env at runtime; pyright doesn't see this.
settings = Settings()  # pyright: ignore[reportCallIssue]
