from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from auth_service.data_sources import data_sources
from auth_service.domain import event, model

if TYPE_CHECKING:
    import motor.motor_asyncio as motor


class AbstractAuthRepository(ABC):
    def __init__(self, *args, **kwargs):
        self.events: list[event.Event] = []

    @abstractmethod
    async def set_user_beak_shape(
        self, user_id: model.UserID, beak_shape: model.BeakShape
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_beak_shape(
        self, beak_shape: model.BeakShape
    ) -> model.UserID | None:
        raise NotImplementedError


class MongoDbAuthRepository(AbstractAuthRepository):
    def __init__(self, motor_client: "motor.AsyncIOMotorClient") -> None:
        super().__init__()
        self.motor_client: "motor.AsyncIOMotorClient" = motor_client
        self.database: "motor.AsyncIOMotorDatabase" = (
            motor_client.get_default_database()
        )
        self.collection: "motor.AsyncIOMotorCollection" = self.database["auth"]

    async def set_user_beak_shape(
        self, user_id: model.UserID, beak_shape: model.BeakShape
    ) -> None:
        query = {
            "_id": beak_shape,
        }
        document = {
            "_id": beak_shape,
            "user_id": user_id,
        }

        await self.collection.replace_one(query, document, upsert=True)

    async def get_user_by_beak_shape(
        self, beak_shape: model.BeakShape
    ) -> model.UserID | None:
        document = await self.collection.find_one({"_id": beak_shape})
        if not document:
            return None

        return model.UserID(document["user_id"])


async def get_auth_repository() -> AbstractAuthRepository:
    motor_client = await data_sources.get_mongodb_client()
    user_repository = MongoDbAuthRepository(motor_client)

    return user_repository
