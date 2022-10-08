from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import uuid4

from task_tracker.data_sources import data_sources
from task_tracker.domain import model, event

if TYPE_CHECKING:
    import motor.motor_asyncio as motor


class AbstractTaskRepository(ABC):
    def __init__(self, *args, **kwargs):
        self.events: list[event.Event] = []

    @abstractmethod
    async def get_tasks(
        self,
        status: model.TaskStatus | None = None,
        user_id: model.UserPublicID | None = None,
    ) -> list[model.Task]:
        raise NotImplementedError

    @abstractmethod
    async def create_task(self, request: model.CreateTaskRequest) -> model.Task:
        raise NotImplementedError

    @abstractmethod
    async def update_task(self, task: model.Task) -> model.Task:
        raise NotImplementedError


class MongoDbTaskRepository(AbstractTaskRepository):
    def __init__(self, motor_client: "motor.AsyncIOMotorClient"):
        super().__init__()
        self.motor_client: "motor.AsyncIOMotorClient" = motor_client
        self.database: "motor.AsyncIOMotorDatabase" = (
            self.motor_client.get_default_database()
        )
        self.collection: "motor.AsyncIOMotorCollection" = self.database["task"]

    async def get_tasks(
        self,
        status: model.TaskStatus | None = None,
        user_id: model.UserPublicID | None = None,
    ) -> list[model.Task]:
        query = {}
        if status:
            query["status"] = status

        if user_id:
            query["user_id"] = user_id

        result = []
        cursor = self.collection.find(query)
        async for document in cursor:
            result.append(
                model.Task(
                    description=document["description"],
                    public_id=model.TaskPublicID(document["public_id"]),
                    status=model.TaskStatus(document["status"]),
                    user_id=model.UserPublicID(document["user_id"]),
                )
            )

        return result

    async def create_task(self, request: model.CreateTaskRequest) -> model.Task:
        public_id = uuid4().hex
        document = {
            "user_id": request.user_id,
            "description": request.description,
            "public_id": public_id,
            "status": model.TaskStatus.open,
        }
        await self.collection.insert_one(document)

        create_event = event.TaskCreated(
            description=request.description,
            public_id=model.TaskPublicID(public_id),
            status=model.TaskStatus.open,
            user_id=request.user_id,
        )
        self.events.append(create_event)

        return model.Task(
            description=request.description,
            public_id=model.TaskPublicID(public_id),
            status=model.TaskStatus.open,
            user_id=request.user_id,
        )

    async def update_task(self, task: model.Task) -> model.Task:
        query = {"public_id": task.public_id}
        document = {
            "user_id": task.user_id,
            "description": task.description,
            "public_id": task.public_id,
            "status": model.TaskStatus.open,
        }

        await self.collection.replace_one(query, document)

        update_event = event.TaskUpdated(
            description=task.description,
            public_id=task.public_id,
            status=task.status,
            user_id=task.user_id,
        )
        self.events.append(update_event)

        return task


async def get_task_repository() -> AbstractTaskRepository:
    motor_client = await data_sources.get_mongodb_client()
    task_repository = MongoDbTaskRepository(motor_client)

    return task_repository
