from typing import Callable

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .centraldvc_entity import CentralDvcEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up CentralDvc sensors from a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    client.register_entity_type(1, CentralDvcSensor, async_add_entities)  # Analog


class CentralDvcSensor(SensorEntity, CentralDvcEntity):
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
        self._state = io["Value"]
        self._units = io["Units"]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._units

    def io_changed(self, io):
        """Update the sensor state and availability from the new IO data."""
        self._state = io["Value"]
