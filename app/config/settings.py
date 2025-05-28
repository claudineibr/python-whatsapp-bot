from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NGROK_AUTHTOKEN: str

    # WhatsApp
    ACCESS_TOKEN: str
    VERIFY_TOKEN: str
    APP_SECRET: str
    APP_ID: str
    RECIPIENT_WAID: str
    PHONE_NUMBER_ID: str
    VERSION: str

    # OPENAI - ChatGPT
    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: str

    DATABASE_URL: str
    ASYNC_DATABASE_URI: str
    SECRET_KEY: str

    DEBUG: bool = False
    ENV: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()
