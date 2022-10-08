from typing import Callable, Awaitable

from task_tracker.domain import model, event
from task_tracker.service_layer.unit_of_work import AbstractUnitOfWork


async def get_user_by_public_id(
    uow: AbstractUnitOfWork, public_id: model.UserPublicID
) -> model.User | None:
    user = await uow.users.get_user_by_public_id(public_id)
    return user


async def handle_user_upsert(
    uow: AbstractUnitOfWork, user_event: event.UserCreated | event.UserUpdated
) -> None:
    user = model.User(
        public_id=user_event.public_id,
        role=user_event.role,
        email=user_event.email,
    )

    await uow.users.upsert_user(user)


async def handle_user_delete(
    uow: AbstractUnitOfWork, user_event: event.UserDeleted
) -> None:
    await uow.users.delete_user(user_event.public_id)


T_EventHandler = Callable[[AbstractUnitOfWork, event.Event], Awaitable[None]]
EVENT_HANDLERS: dict[event.Event, list[T_EventHandler]] = {
    event.UserCreated: [handle_user_upsert],
    event.UserUpdated: [handle_user_upsert],
    event.UserDeleted: [handle_user_delete],
}
