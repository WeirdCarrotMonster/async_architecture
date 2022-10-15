# generated by datamodel-codegen:
#   filename:  1.json
#   timestamp: 2022-10-15T15:18:55+00:00

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class UserRole(Enum):
    admin = 'admin'
    manager = 'manager'
    accountant = 'accountant'


class UserCreated(BaseModel):
    public_id: str = Field(..., title='Public Id')
    role: UserRole
    email: str = Field(..., title='Email')
