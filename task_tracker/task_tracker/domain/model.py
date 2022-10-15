from dataclasses import dataclass
from enum import Enum
from typing import NewType


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    accountant = "accountant"


UserEmail = NewType("UserEmail", str)
UserPublicID = NewType("UserPublicID", str)


@dataclass
class User:
    public_id: UserPublicID
    role: UserRole
    email: UserEmail


class TaskStatus(str, Enum):
    open = "open"
    closed = "closed"


TaskPublicID = NewType("TaskPublicId", str)


@dataclass
class Task:
    public_id: TaskPublicID
    user_id: UserPublicID
    status: TaskStatus
    description: str


@dataclass
class CreateTaskRequest:
    user_id: UserPublicID
    description: str
