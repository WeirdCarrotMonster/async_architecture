from typing import Type

from pydantic import BaseModel

from task_tracker.domain.event.task.task_added.v1 import TaskAdded
from task_tracker.domain.event.task.task_assigned.v1 import TaskAssigned
from task_tracker.domain.event.task.task_closed.v1 import TaskClosed
from task_tracker.domain.event.task.task_created.v1 import TaskCreated
from task_tracker.domain.event.task.task_shuffle_requested.v1 import (
    TaskShuffleRequested,
)
from task_tracker.domain.event.task.task_updated.v1 import TaskUpdated
from task_tracker.domain.event.user.user_created.v1 import UserCreated
from task_tracker.domain.event.user.user_deleted.v1 import UserDeleted
from task_tracker.domain.event.user.user_updated.v1 import UserUpdated

EVENTS: tuple[tuple[str, int, Type], ...] = (
    ("User.UserCreated", 1, UserCreated),
    ("User.UserUpdated", 1, UserUpdated),
    ("User.UserDeleted", 1, UserDeleted),
    ("Task.TaskCreated", 1, TaskCreated),
    ("Task.TaskUpdated", 1, TaskUpdated),
    ("Task.TaskAdded", 1, TaskAdded),
    ("Task.TaskAssigned", 1, TaskAssigned),
    ("Task.TaskClosed", 1, TaskClosed),
    ("Task.TaskShuffleRequested", 1, TaskShuffleRequested),
)


EVENT_VERSION_MAP = {(name, version): cls for name, version, cls in EVENTS}
EVENT_TOPIC_MAP = {cls: f"{name}.{version}" for name, version, cls in EVENTS}
EVENT_NAME_VERSION_MAP = {cls: (name, version) for name, version, cls in EVENTS}


def get_event_cls(name: str, version: int) -> Type | None:
    return EVENT_VERSION_MAP.get((name, version))


def get_event_topic(cls: Type) -> str:
    return EVENT_TOPIC_MAP[cls]


def get_event_name_version(cls: Type) -> tuple[str, int]:
    return EVENT_NAME_VERSION_MAP[cls]
