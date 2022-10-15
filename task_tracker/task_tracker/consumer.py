import asyncio
from json import loads

from nats.errors import TimeoutError
from pydantic import BaseModel

from task_tracker.data_sources import data_sources
from task_tracker.domain.event.builder import get_event_cls
from task_tracker.service_layer import user as user_service
from task_tracker.service_layer.unit_of_work import get_unit_of_work


def parse_event(payload: bytes) -> BaseModel | None:
    parsed = loads(payload)

    name = parsed["name"]
    version = parsed["version"]
    data = parsed["data"]

    cls = get_event_cls(name, version)

    if not cls:
        return None

    return cls(**data)


def get_event_handlers(event: BaseModel):
    event_cls = event.__class__
    handlers = user_service.EVENT_HANDLERS.get(event_cls)
    return handlers


async def on_message(message) -> None:
    print(f"Handling message {message}")
    await message.ack()

    event = parse_event(message.data)
    if not event:
        print(f"Cannot parse message into event; skipping: {message}")
        return

    handlers = get_event_handlers(event)
    if not handlers:
        print(f"Event has no handlers; skipping: {event}")
        return

    for handler in handlers:
        print(f"Calling {handler}...")
        uow = await get_unit_of_work()
        async with uow:
            await handler(uow, event)


async def run_consumer():
    print("Starting consumer")
    nats_client = await data_sources.get_nats_client()
    jetstream = nats_client.jetstream()

    await jetstream.subscribe(
        "User.>", stream="default", durable="task_tracker", cb=on_message
    )
    while True:
        await asyncio.sleep(1)
