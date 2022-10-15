from dataclasses import dataclass
from enum import Enum
from typing import NewType


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    accountant = "accountant"


UserID = NewType("UserID", str)
UserEmail = NewType("UserEmail", str)
UserPublicID = NewType("UserPublicID", str)
BeakShape = NewType("BeakShape", str)


@dataclass
class User:
    id: UserID
    public_id: UserPublicID
    role: UserRole
    email: UserEmail


@dataclass
class Auth:
    user_id: UserID
    beak_shape: BeakShape


@dataclass
class CreateUserRequest:
    role: UserRole
    beak_shape: BeakShape
    email: UserEmail


@dataclass
class UpdateUserRequest:
    role: UserRole
    beak_shape: BeakShape
    email: UserEmail


@dataclass
class AuthenticateUserRequest:
    beak_shape: BeakShape


@dataclass
class DeleteUserRequest:
    id: UserID
