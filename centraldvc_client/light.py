from collections.abc import Callable

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entities_base.centraldvc_entity import CentralDvcEntity
from .entities_base.entity_definition import EntityDefinition


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up CentralDvc sensors from a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    client.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcLight, async_add_entities, None, lambda io: io["Kind"] == 2
        ),
    )  # Light


class CentralDvcLight(LightEntity, CentralDvcEntity):
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
        self._attr_supported_color_modes = [ColorMode.ONOFF]

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        self.set_io("1:1")

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self.set_io("1:2")

    def io_changed(self, io):
        """Update the sensor state and availability from the new IO data."""
        self._state = io["Value"]
