from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_uri: str = (
        "mongodb://root:password@127.0.0.1:27017/task_tracker?authSource=admin"
    )
    nats_uri: str = "nats://127.0.0.1:4222"


settings = Settings()
