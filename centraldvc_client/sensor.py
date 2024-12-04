from typing import List

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
    # This function will set up sensor entities when the config entry is first added.
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    client.register_entity_type(1, CentralDvcAnalogSensor, async_add_entities)


#  entities = list(hass.data[DOMAIN][entry.entry_id]["entities"].values())

# if entities:
# Add any entities that are currently known
#    async_add_entities(entities)


class CentralDvcAnalogSensor(SensorEntity, CentralDvcEntity):
    def __init__(self, id, config_entry, hass, io):
        """Initialize the analog sensor."""
        super().__init__(id, config_entry, hass, io)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._is_online

    #  @property
    # def device_class(self):
    #    """Return the device class if appropriate."""
    #   return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._units

    def io_changed(self, io):
        """Update the sensor state and availability from the new IO data."""
        self._state = io["Value"]
        self._is_online = io["IsOnline"]
