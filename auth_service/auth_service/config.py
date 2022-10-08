from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_uri: str = "mongodb://127.0.0.1:27017/auth_service"
    nats_uri: str = "nats://nats:4222"


settings = Settings()
