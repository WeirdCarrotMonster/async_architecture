from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from task_tracker.data_sources import data_sources
from task_tracker.domain import model, event

if TYPE_CHECKING:
    import motor.motor_asyncio as motor


class AbstractUserRepository(ABC):
    def __init__(self, *args, **kwargs):
        self.events: list[event.Event] = []

    @abstractmethod
    async def get_user_by_public_id(
        self, user_public_id: model.UserPublicID
    ) -> model.User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_random_user(
        self, roles: list[model.UserRole] | None = None
    ) -> model.User | None:
        raise NotImplementedError

    @abstractmethod
    async def upsert_user(self, user: model.User) -> model.User:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_public_id: model.UserPublicID) -> None:
        raise NotImplementedError


class MongoDbUserRepository(AbstractUserRepository):
    def __init__(self, motor_client: "motor.AsyncIOMotorClient") -> None:
        super().__init__()
        self.motor_client: "motor.AsyncIOMotorClient" = motor_client
        self.database: "motor.AsyncIOMotorDatabase" = (
            motor_client.get_default_database()
        )
        self.collection: "motor.AsyncIOMotorCollection" = self.database["user"]

    async def get_user_by_public_id(
        self, user_public_id: model.UserPublicID
    ) -> model.User | None:
        document = await self.collection.find_one({"public_id": user_public_id})

        if not document:
            return None

        return model.User(
            email=model.UserEmail(document["email"]),
            public_id=model.UserPublicID(document["public_id"]),
            role=model.UserRole(document["role"]),
        )

    async def get_random_user(
        self, roles: list[model.UserRole] | None = None
    ) -> model.User | None:
        pipeline: list[dict] = []
        if roles:
            pipeline.append({"$match": {"role": {"$in": roles}}})

        pipeline.append({"$sample": {"size": 1}})

        document = None
        async for document in self.collection.aggregate(pipeline):
            pass

        if not document:
            return None

        return model.User(
            email=model.UserEmail(document["email"]),
            public_id=model.UserPublicID(document["public_id"]),
            role=model.UserRole(document["role"]),
        )

    async def upsert_user(self, user: model.User) -> model.User:
        query = {"public_id": user.public_id}
        replace_data = {
            "public_id": user.public_id,
            "email": user.email,
            "role": user.role,
        }
        await self.collection.replace_one(query, replace_data, upsert=True)

        return user

    async def delete_user(self, user_public_id: model.UserPublicID) -> None:
        await self.collection.delete_one({"public_id": user_public_id})


async def get_user_repository() -> AbstractUserRepository:
    motor_client = await data_sources.get_mongodb_client()
    user_repository = MongoDbUserRepository(motor_client)

    return user_repository
