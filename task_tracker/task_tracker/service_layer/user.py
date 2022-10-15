from task_tracker.domain import model
from task_tracker.domain.event.user.user_created.v1 import UserCreated
from task_tracker.domain.event.user.user_deleted.v1 import UserDeleted
from task_tracker.domain.event.user.user_updated.v1 import UserUpdated
from task_tracker.service_layer.unit_of_work import AbstractUnitOfWork


async def get_user_by_public_id(
    uow: AbstractUnitOfWork, public_id: model.UserPublicID
) -> model.User | None:
    user = await uow.users.get_user_by_public_id(public_id)
    return user


async def handle_user_upsert(
    uow: AbstractUnitOfWork, user_event: UserCreated | UserUpdated
) -> None:
    user = model.User(
        public_id=model.UserPublicID(user_event.public_id),
        role=user_event.role,
        email=model.UserEmail(user_event.email),
    )

    await uow.users.upsert_user(user)


async def handle_user_delete(uow: AbstractUnitOfWork, user_event: UserDeleted) -> None:
    await uow.users.delete_user(model.UserPublicID(user_event.public_id))


EVENT_HANDLERS = {
    UserCreated: [handle_user_upsert],
    UserUpdated: [handle_user_upsert],
    UserDeleted: [handle_user_delete],
}
