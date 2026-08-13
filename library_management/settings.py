from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES_TIME: int
    TOKEN_SECRET_KEY: str
    ALGORITHM: str
    MAX_VALUE_LOANS: int
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
