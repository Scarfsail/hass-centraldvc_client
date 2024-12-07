import json
import logging
import threading

from signalrcore.hub_connection_builder import HubConnectionBuilder

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import run_callback_threadsafe

from ..entities_base.entity_definition import EntityDefinition

_LOGGER = logging.getLogger(__name__)


class CentralDvcClient:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        url = entry.data["url"]
        self.hub = (
            HubConnectionBuilder().with_url(url, options={"verify_ssl": False}).build()
        )
        self.entity_definitions_by_visualization = {}
        self.entities = {}

    async def start(self):
        await self.hass.async_add_executor_job(self.hub.start)
        send_callback_received = threading.Lock()

        def callback(response):
            self.process_initial_load(response)
            self.hub.on("iosChanged", self.process_iosChanged)

            send_callback_received.release()

        self.hub.send("GetAllIos", [], callback)

        if not send_callback_received.acquire(timeout=10):
            raise ValueError("CALLBACK NOT RECEIVED")

    def stop(self):
        self.hub.stop()

    def process_initial_load(self, response):
        data = json.loads(response.result)
        self.process_data_update(data)

    def process_iosChanged(self, response):
        data = json.loads(response[0])
        self.process_data_update(data)

    def register_entity_type(
        self, io_visualization: int, entity_definition: EntityDefinition
    ):
        if io_visualization in self.entity_definitions_by_visualization:
            self.entity_definitions_by_visualization[io_visualization].append(
                entity_definition
            )
        else:
            self.entity_definitions_by_visualization[io_visualization] = [
                entity_definition
            ]

    def create_entity(self, entity_definition: EntityDefinition, io):
        io_id = io["Id"]
        entity_id = f"centraldvc_{io_id}"
        entity = entity_definition.entity_class(
            entity_id,
            self.entry,
            self.hass,
            io,
            self.set_io,
            entity_definition.device_class,
        )
        run_callback_threadsafe(
            self.hass.loop, entity_definition.async_add_entities, [entity]
        )
        return entity

    def set_io(self, io_id: int, value: str) -> None:
        self.hub.send("SetIo", [{"IoId": io_id, "Value": value, "Answers": []}])

    def process_data_update(self, data):
        """Process incoming data and create/update entities accordingly."""

        for io in data:
            io_id = io["Id"]
            entity_id = f"centraldvc_{io_id}"
            entity = self.entities.get(entity_id)
            if entity:
                entity.update_from_io(io)
                continue

            visualization = io.get("Visualization")
            entity_definitions = self.entity_definitions_by_visualization.get(
                visualization
            )
            if not entity_definitions:
                _LOGGER.warning(
                    f"No entity definitions for visualization: {visualization} with io ID: {io_id}"  # noqa: G004
                )
                continue
            entity = None

            for entity_definition in entity_definitions:
                if not entity_definition.selector:
                    if len(entity_definitions) > 1:
                        _LOGGER.warning(
                            f"Selector is not specified for entity visualization: {visualization} with multiple definitions. IO ID: {io_id}"
                        )  # noqa: G004
                    else:
                        entity = self.create_entity(entity_definition, io)
                        break
                elif entity_definition.selector(io):
                    entity = self.create_entity(entity_definition, io)
                    break

            if entity is not None:
                self.entities[entity_id] = entity
                _LOGGER.info(f"Created entity for io: {io["Title"]}")
            else:
                _LOGGER.warning(
                    f"No entity definition found for visualization: {visualization} with io ID: {io_id}"
                )  # noqa: G004
