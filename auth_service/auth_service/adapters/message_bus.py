import uuid
from abc import ABC, abstractmethod
from json import dumps, loads
from typing import TYPE_CHECKING

from pydantic import BaseModel

from auth_service.data_sources import data_sources
from auth_service.domain.event.builder import get_event_name_version, get_event_topic

if TYPE_CHECKING:
    import nats
    import nats.js


class AbstractMessageBus(ABC):
    @abstractmethod
    async def send_event(self, event: BaseModel) -> None:
        raise NotImplementedError


class NatsMessageBus(AbstractMessageBus):
    def __init__(self, nats_client: "nats.NATS") -> None:
        self.nats_client: "nats.NATS" = nats_client
        self.jetstream: "nats.js.JetStreamContext" = nats_client.jetstream()

    async def send_event(self, event: BaseModel) -> None:
        event_cls = event.__class__
        name, version = get_event_name_version(event_cls)

        payload_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "version": version,
            "data": loads(event.json()),
        }

        payload_bytes = dumps(payload_data).encode()
        subject = get_event_topic(event_cls)

        await self.jetstream.publish(subject, payload=payload_bytes)


async def get_message_bus() -> AbstractMessageBus:
    nats_client = await data_sources.get_nats_client()
    message_bus = NatsMessageBus(nats_client)

    return message_bus
