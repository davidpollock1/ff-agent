from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    ECHO_SQL: bool = False


settings = Settings()
