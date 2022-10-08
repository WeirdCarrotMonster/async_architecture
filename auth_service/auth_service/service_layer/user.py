from auth_service.domain import model
from auth_service.service_layer.unit_of_work import AbstractUnitOfWork


async def create_user(
    uow: AbstractUnitOfWork, request: model.CreateUserRequest
) -> model.User:
    user = await uow.users.create_user(request)
    await uow.auths.set_user_beak_shape(user.id, request.beak_shape)

    await uow.commit()
    return user


async def get_user(uow: AbstractUnitOfWork, user_id: model.UserID) -> model.User | None:
    user = await uow.users.get_user_by_id(user_id)
    return user


async def update_user(
    uow: AbstractUnitOfWork, user_id: model.UserID, request: model.UpdateUserRequest
) -> model.User:
    user = await uow.users.get_user_by_id(user_id)

    user.role = request.role
    user.email = request.email

    await uow.users.update_user(user)
    await uow.auths.set_user_beak_shape(user.id, request.beak_shape)

    await uow.commit()
    return user


async def delete_user(
    uow: AbstractUnitOfWork, request: model.DeleteUserRequest
) -> None:
    user = await uow.users.get_user_by_id(request.id)

    await uow.users.delete_user(user)

    await uow.commit()


async def authenticate_user(
    uow: AbstractUnitOfWork, request: model.AuthenticateUserRequest
) -> model.User | None:
    user_id = await uow.auths.get_user_by_beak_shape(request.beak_shape)
    if not user_id:
        return None

    user = await uow.users.get_user_by_id(user_id)
    return user
