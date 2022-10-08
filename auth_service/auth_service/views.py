from fastapi import APIRouter, Depends, HTTPException

from auth_service.domain import model
from auth_service.service_layer.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from auth_service.service_layer import user as user_service


router = APIRouter()


@router.get("/user/{user_id}", response_model=model.User)
async def get_user_by_id(
    user_id: model.UserID,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        user = await user_service.get_user(uow, user_id)

    if not user:
        raise HTTPException(status_code=404)

    return user


@router.post("/user", response_model=model.User)
async def create_user(
    request: model.CreateUserRequest,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        user = await user_service.create_user(uow, request)

    return user


@router.put("/user/{user_id}", response_model=model.User)
async def update_user(
    user_id: model.UserID,
    request: model.UpdateUserRequest,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        user = await user_service.update_user(uow, user_id, request)

    return user
