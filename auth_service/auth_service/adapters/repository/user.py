from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import uuid4

from bson import ObjectId
from pydantic import BaseModel

from auth_service.data_sources import data_sources
from auth_service.domain import model
from auth_service.domain.event.user.user_created.v1 import UserCreated
from auth_service.domain.event.user.user_deleted.v1 import UserDeleted
from auth_service.domain.event.user.user_updated.v1 import UserUpdated

if TYPE_CHECKING:
    import motor.motor_asyncio as motor


class AbstractUserRepository(ABC):
    def __init__(self, *args, **kwargs):
        self.events: list[BaseModel] = []

    @abstractmethod
    async def get_user_by_id(self, user_id: model.UserID) -> model.User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_public_id(
        self, user_public_id: model.UserPublicID
    ) -> model.User | None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, request: model.CreateUserRequest) -> model.User:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: model.User) -> model.User:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user: model.User) -> None:
        raise NotImplementedError


class MongoDbUserRepository(AbstractUserRepository):
    def __init__(self, motor_client: "motor.AsyncIOMotorClient") -> None:
        super().__init__()
        self.motor_client: "motor.AsyncIOMotorClient" = motor_client
        self.database: "motor.AsyncIOMotorDatabase" = (
            motor_client.get_default_database()
        )
        self.collection: "motor.AsyncIOMotorCollection" = self.database["user"]

    async def get_user_by_id(self, user_id: model.UserID) -> model.User | None:
        document = await self.collection.find_one({"_id": ObjectId(user_id)})

        if not document:
            return None

        return model.User(
            id=model.UserID(str(document["_id"])),
            email=model.UserEmail(document["email"]),
            public_id=model.UserPublicID(document["public_id"]),
            role=model.UserRole(document["role"]),
        )

    async def get_user_by_public_id(
        self, user_public_id: model.UserPublicID
    ) -> model.User | None:
        document = await self.collection.find_one({"public_id": user_public_id})

        if not document:
            return None

        return model.User(
            id=model.UserID(document["_id"]),
            email=model.UserEmail(document["email"]),
            public_id=model.UserPublicID(document["public_id"]),
            role=model.UserRole(document["role"]),
        )

    async def create_user(self, request: model.CreateUserRequest) -> model.User:
        public_id = uuid4().hex
        document = {
            "email": request.email,
            "public_id": public_id,
            "role": request.role,
        }
        result = await self.collection.insert_one(document)
        user_id = model.UserID(str(result.inserted_id))

        user = model.User(
            id=user_id,
            public_id=model.UserPublicID(public_id),
            email=request.email,
            role=request.role,
        )

        create_event = UserCreated(
            public_id=user.public_id,
            role=user.role,
            email=user.email,
        )

        self.events.append(create_event)
        return user

    async def update_user(self, user: model.User) -> model.User:
        update_data = {
            "email": user.email,
            "role": user.role,
        }
        await self.collection.update_one({"_id": user.id}, {"$set": update_data})
        user = model.User(
            id=user.id,
            public_id=user.public_id,
            email=user.email,
            role=user.role,
        )

        update_event = UserUpdated(
            public_id=user.public_id,
            role=user.role,
            email=user.email,
        )

        self.events.append(update_event)
        return user

    async def delete_user(self, user: model.User) -> None:
        delete_event = UserDeleted(public_id=user.public_id)

        self.events.append(delete_event)
        await self.collection.delete_one({"_id": user.id})


async def get_user_repository() -> AbstractUserRepository:
    motor_client = await data_sources.get_mongodb_client()
    user_repository = MongoDbUserRepository(motor_client)

    return user_repository
