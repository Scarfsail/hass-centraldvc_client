from collections.abc import Callable
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import run_callback_threadsafe

from ..entities_base.entity_definition import EntityDefinition

_LOGGER = logging.getLogger(__name__)


class CentralDvcDataProcessor:
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        set_io: Callable[[int, str], None],
    ):
        self.hass = hass
        self.entry = entry
        self.set_io = set_io
        self.entity_definitions_by_visualization = {}
        self.entities = {}

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

    def set_all_entities_offline(self):
        for entities in self.entities.values():
            for entity in entities:
                entity.set_is_offline()

    def process_data_update(self, data):
        """Process incoming data and create/update entities accordingly."""

        for io in data:
            io_id = io["Id"]
            entity_id = f"centraldvc_{io_id}"
            entities = self.entities.get(entity_id)
            if entities:
                for entity in entities:
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
            # entity = None
            entities = []
            for entity_definition in entity_definitions:
                if not entity_definition.selector or entity_definition.selector(io):
                    entity = self.create_entity(entity_definition, io)
                    entities.append(entity)

            if len(entities) > 0:
                self.entities[entity_id] = entities
                _LOGGER.info(f"Created {len(entities)} entities for io: {io["Title"]}")
            else:
                _LOGGER.warning(
                    f"No entity definition found for visualization: {visualization} with io ID: {io_id}"
                )  # noqa: G004
