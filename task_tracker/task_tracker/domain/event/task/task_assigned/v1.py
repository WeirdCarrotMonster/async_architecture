# generated by datamodel-codegen:
#   filename:  1.json
#   timestamp: 2022-10-15T15:14:48+00:00

from __future__ import annotations

from pydantic import BaseModel, Field


class TaskAssigned(BaseModel):
    public_id: str = Field(..., title='Public Id')
    user_id: str = Field(..., title='User Id')
