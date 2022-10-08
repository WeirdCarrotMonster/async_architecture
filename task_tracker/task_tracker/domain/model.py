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
