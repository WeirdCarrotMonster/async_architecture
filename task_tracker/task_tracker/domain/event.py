from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

from task_tracker.domain import model


@dataclass
class Event(ABC):
    @classmethod
    @abstractmethod
    def get_topic_name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_event_name(cls) -> str:
        return cls.__name__

    def get_data(self) -> dict:
        return asdict(self)


@dataclass
class UserCreated(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "cud.user"

    public_id: model.UserPublicID
    role: model.UserRole
    email: model.UserEmail


@dataclass
class UserUpdated(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "cud.user"

    public_id: model.UserPublicID
    role: model.UserRole
    email: model.UserEmail


@dataclass
class UserDeleted(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "cud.user"

    public_id: model.UserPublicID


@dataclass
class TaskCreated(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "cud.task"

    public_id: model.TaskPublicID
    user_id: model.UserPublicID
    status: model.TaskStatus
    description: str


@dataclass
class TaskUpdated(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "cud.task"

    public_id: model.TaskPublicID
    user_id: model.UserPublicID
    status: model.TaskStatus
    description: str


@dataclass
class TaskAdded(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "be.task"

    public_id: model.TaskPublicID
    user_id: model.UserPublicID
    status: model.TaskStatus
    description: str


@dataclass
class TaskAssigned(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "be.task"

    public_id: model.TaskPublicID
    user_id: model.UserPublicID


@dataclass
class TaskClosed(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "be.task"

    public_id: model.TaskPublicID


@dataclass
class TaskShuffleRequested(Event):
    @classmethod
    def get_topic_name(cls) -> str:
        return "be.task"

    user_id: model.UserPublicID


EVENT_NAME_MAP = {
    "UserCreated": UserCreated,
    "UserUpdated": UserUpdated,
    "UserDeleted": UserDeleted,
    "TaskShuffleRequested": TaskShuffleRequested,
}


def get_event_cls_by_name(name: str) -> Event | None:
    return EVENT_NAME_MAP.get(name)
