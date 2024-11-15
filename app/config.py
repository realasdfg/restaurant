from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    db_uri: str
    secret_key: str
    jwt_algorithm: str = 'HS256'
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 3

    # model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
