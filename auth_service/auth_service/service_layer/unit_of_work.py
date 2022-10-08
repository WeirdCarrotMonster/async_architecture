from abc import ABC
from itertools import chain

from auth_service.adapters.message_bus import AbstractMessageBus, get_message_bus
from auth_service.domain.event import Event
from auth_service.adapters.repository.user import (
    AbstractUserRepository,
    get_user_repository,
)
from auth_service.adapters.repository.auth import (
    AbstractAuthRepository,
    get_auth_repository,
)


class AbstractUnitOfWork(ABC):
    message_bus: AbstractMessageBus
    users: AbstractUserRepository
    auths: AbstractAuthRepository

    def __init__(self, *args, **kwargs) -> None:
        self.events: list[Event] = []

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

    async def commit(self) -> None:
        event_chain = chain(self.users.events, self.auths.events, self.events)

        for event in event_chain:
            await self.message_bus.send_event(event)


class UnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        message_bus: AbstractMessageBus,
        users: AbstractUserRepository,
        auths: AbstractAuthRepository,
    ):
        super().__init__()
        self.message_bus = message_bus
        self.users = users
        self.auths = auths


async def get_unit_of_work() -> AbstractUnitOfWork:
    message_bus = await get_message_bus()
    users = await get_user_repository()
    auths = await get_auth_repository()

    return UnitOfWork(message_bus=message_bus, users=users, auths=auths)
