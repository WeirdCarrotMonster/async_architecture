from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from json import dumps

from auth_service.data_sources import data_sources
from auth_service.domain.event import Event

if TYPE_CHECKING:
    import nats
    import nats.js


class AbstractMessageBus(ABC):
    @abstractmethod
    async def send_event(self, event: Event) -> None:
        raise NotImplementedError


class NatsMessageBus(AbstractMessageBus):
    def __init__(self, nats_client: "nats.NATS") -> None:
        self.nats_client: "nats.NATS" = nats_client
        self.jetstream: "nats.js.JetStreamContext" = nats_client.jetstream()

    async def send_event(self, event: Event) -> None:
        payload_data = {
            "name": event.get_event_name(),
            "data": event.get_data(),
        }
        payload_bytes = dumps(payload_data).encode()
        subject = event.get_topic_name()

        await self.jetstream.publish(subject, payload=payload_bytes)


async def get_message_bus() -> AbstractMessageBus:
    nats_client = await data_sources.get_nats_client()
    message_bus = NatsMessageBus(nats_client)

    return message_bus
