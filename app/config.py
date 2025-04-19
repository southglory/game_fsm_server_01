from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    fsm_definitions_path: str = "fsm_definitions"

    class Config:
        env_file = ".env"


settings = Settings()
