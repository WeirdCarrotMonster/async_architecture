from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth_service.config import settings
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


class AuthResponse(BaseModel):
    token: str


@router.post("/auth", response_model=AuthResponse)
async def authenticate_user(
    request: model.AuthenticateUserRequest,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    async with uow:
        user = await user_service.authenticate_user(uow, request)

    if not user:
        raise HTTPException(status_code=403)

    expires = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {"public_id": user.public_id, "exp": expires}, settings.auth_secret
    )
    return AuthResponse(token=token)
