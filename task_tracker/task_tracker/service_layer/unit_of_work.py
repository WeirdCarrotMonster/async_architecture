from abc import ABC
from itertools import chain

from task_tracker.adapters.message_bus import AbstractMessageBus, get_message_bus
from task_tracker.domain.event import Event
from task_tracker.adapters.repository.user import (
    AbstractUserRepository,
    get_user_repository,
)
from task_tracker.adapters.repository.task import (
    AbstractTaskRepository,
    get_task_repository,
)


class AbstractUnitOfWork(ABC):
    message_bus: AbstractMessageBus
    users: AbstractUserRepository
    tasks: AbstractTaskRepository

    def __init__(self, *args, **kwargs) -> None:
        self.events: list[Event] = []

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

    async def commit(self) -> None:
        event_chain = chain(self.users.events, self.tasks.events, self.events)

        for event in event_chain:
            await self.message_bus.send_event(event)


class UnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        message_bus: AbstractMessageBus,
        users: AbstractUserRepository,
        tasks: AbstractTaskRepository,
    ):
        super().__init__()
        self.message_bus = message_bus
        self.users = users
        self.tasks = tasks


async def get_unit_of_work() -> AbstractUnitOfWork:
    message_bus = await get_message_bus()
    users = await get_user_repository()
    tasks = await get_task_repository()

    return UnitOfWork(message_bus=message_bus, users=users, tasks=tasks)
