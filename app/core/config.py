import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./stock_analysis.db")
    secret_key: str = os.getenv("SECRET_KEY", "local-development-only")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    fastapi_server_port: int = int(os.getenv("FASTAPI_SERVER_PORT", 8000))
    streamlit_server_port: int = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()