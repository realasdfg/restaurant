from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    db_uri: str
    secret_key: str
    jwt_algorithm: str = 'HS256'
    access_token_expires_hours: int = 2
    refresh_token_expires_days: int = 3
    file_upload_dir: str = '..\\restaurant_frontend\\public\\images'

    # model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
