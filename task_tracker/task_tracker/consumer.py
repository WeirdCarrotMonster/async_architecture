import asyncio
from json import loads

from nats.errors import TimeoutError

from task_tracker.data_sources import data_sources
from task_tracker.domain.event import Event, get_event_cls_by_name
from task_tracker.service_layer import user as user_service
from task_tracker.service_layer.unit_of_work import get_unit_of_work


def parse_event(payload: bytes) -> Event | None:
    parsed = loads(payload)
    name = parsed["name"]
    data = parsed["data"]

    cls = get_event_cls_by_name(name)
    if not cls:
        return None

    return cls(**data)


def get_event_handlers(event: Event):
    event_cls = event.__class__
    handlers = user_service.EVENT_HANDLERS.get(event_cls)
    return handlers


async def run_consumer():
    print("Starting consumer")
    nats_client = await data_sources.get_nats_client()
    jetstream = nats_client.jetstream()

    psub = await jetstream.pull_subscribe("cud.*", "task_tracker")

    while True:
        try:
            print("Fetching message batch...")
            message_batch = await psub.fetch(1, timeout=5)
        except TimeoutError:
            continue

        for message in message_batch:
            await message.ack()

            event = parse_event(message.data)
            if not event:
                print(f"Cannot parse message into event; skipping: {message}")

            handlers = get_event_handlers(event)
            if not handlers:
                print(f"Event has no handlers; skipping: {event}")

            for handler in handlers:
                print(f"Calling {handler}...")
                uow = await get_unit_of_work()
                async with uow:
                    await handler(uow, event)
