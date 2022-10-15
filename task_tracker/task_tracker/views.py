from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import decode
from pydantic import BaseModel, validator

from task_tracker.config import settings
from task_tracker.domain import model
from task_tracker.service_layer import task as task_service
from task_tracker.service_layer import user as user_service
from task_tracker.service_layer.unit_of_work import AbstractUnitOfWork, get_unit_of_work

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
    jira_id: model.TaskJiraID | None = None

    @validator("description")
    def description_must_not_contain_jira_id(cls, v: str):
        if "[" in v or "]" in v:
            raise ValueError("Description must not contain JIRA ID")
        return v


@router.get("/task")
async def get_tasks(
    user: model.User = Depends(get_user),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    kwargs = {}
    if user.role != model.UserRole.admin:
        kwargs["user_id"] = user.public_id

    async with uow:
        tasks = await task_service.get_tasks(
            uow, status=model.TaskStatus.open, **kwargs
        )

    return tasks


@router.post("/task", response_model=model.Task)
async def create_task(
    data: CreateTaskForm,
    user: model.User = Depends(get_user),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        task = await task_service.create_task(
            uow, description=data.description, jira_id=data.jira_id
        )

    return task


@router.post("/task/{task_id}/close", response_model=model.Task)
async def close_task(
    task_id: model.TaskPublicID,
    user: model.User = Depends(get_user),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        task = await task_service.close_task(
            uow, user_id=user.public_id, task_id=task_id
        )

    return task


@router.post("/shuffle", status_code=201)
async def request_task_shuffle(
    user: model.User = Depends(get_user),
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    if user.role != model.UserRole.admin:
        raise HTTPException(status_code=403)

    async with uow:
        await task_service.request_task_shuffle(uow, user_id=user.public_id)
