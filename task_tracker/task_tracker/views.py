from jwt import decode
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from task_tracker.domain import model
from task_tracker.config import settings
from task_tracker.service_layer.unit_of_work import get_unit_of_work, AbstractUnitOfWork
from task_tracker.service_layer import user as user_service
from task_tracker.service_layer import task as task_service


router = APIRouter()
security = HTTPBearer()


async def get_user(
    authorization: HTTPAuthorizationCredentials = Depends(security),
) -> model.User:
    try:
        token = authorization.credentials
        token_data = decode(token, settings.auth_secret, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=403)

    public_id = token_data.get("public_id")
    if not public_id:
        raise HTTPException(status_code=403)

    uow = await get_unit_of_work()
    async with uow:
        user = await user_service.get_user_by_public_id(uow, public_id)

    if not user:
        raise HTTPException(status_code=403)

    return user


@router.get("/whoami", response_model=model.User)
async def get_whoami(user: model.User = Depends(get_user)):
    return user


class CreateTaskForm(BaseModel):
    description: str


@router.post("/task", response_model=model.Task)
async def create_task(
    data: CreateTaskForm,
    user: model.User = Depends(get_user),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        task = await task_service.create_task(uow, description=data.description)

    return task
