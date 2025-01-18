from collections.abc import Callable

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .entities_base.centraldvc_entity import CentralDvcEntity
from .entities_base.entity_definition import EntityDefinition


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up CentralDvc sensors from a config entry."""
    processor = hass.data[DOMAIN][entry.entry_id]["client"].processor
    processor.register_entity_type(
        2, EntityDefinition(CentralDvcBinarySensor, async_add_entities, "door")
    )
    processor.register_entity_type(
        7, EntityDefinition(CentralDvcBinarySensor, async_add_entities, "motion")
    )
    processor.register_entity_type(
        13, EntityDefinition(CentralDvcBinarySensor, async_add_entities)
    )  # Digital
    processor.register_entity_type(
        8, EntityDefinition(CentralDvcBinarySensor, async_add_entities, "garage_door")
    )  # Gate


class CentralDvcBinarySensor(BinarySensorEntity, CentralDvcEntity, RestoreEntity):
    def __init__(
        self,
        id,
        config_entry,
        hass,
        io,
        set_io: Callable[[int, str], None],
        device_clas,
    ):
        """Initialize the sensor."""
        super().__init__(id, config_entry, hass, io, set_io, device_clas)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def io_changed(self, io):
        """Update the sensor state and availability from the new IO data."""
        self._state = "on" if io["Value"] else "off"
        self._state_last_changed = io["LastChange"]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""

        return {
            "state_last_changed": self._state_last_changed,
        }

    async def async_added_to_hass(self):
        """Restore state when the entity is added to hass."""
        await super().async_added_to_hass()
        # Retrieve the previous state

        old_state = await self.async_get_last_state()
        if old_state is not None:
            self._state_last_changed = old_state.attributes.get(
                "state_last_changed", None
            )
