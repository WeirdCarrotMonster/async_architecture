from typing import Type

from auth_service.domain.event.user.user_created.v1 import UserCreated
from auth_service.domain.event.user.user_deleted.v1 import UserDeleted
from auth_service.domain.event.user.user_updated.v1 import UserUpdated

EVENTS: tuple[tuple[str, int, Type], ...] = (
    ("User.UserCreated", 1, UserCreated),
    ("User.UserUpdated", 1, UserUpdated),
    ("User.UserDeleted", 1, UserDeleted),
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
