import nats
import motor.motor_asyncio as motor

from task_tracker.config import settings


class DataSources:
    def __init__(self) -> None:
        self.motor_client: motor.AsyncIOMotorClient | None = None
        self.nats_client: nats.NATS | None = None

    async def get_mongodb_client(self) -> motor.AsyncIOMotorClient:
        if self.motor_client is None:
            self.motor_client = motor.AsyncIOMotorClient(settings.database_uri)
        return self.motor_client

    async def get_nats_client(self) -> nats.NATS:
        if self.nats_client is None:
            self.nats_client = await nats.connect(settings.nats_uri)
        return self.nats_client


data_sources = DataSources()
