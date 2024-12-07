from collections.abc import Callable

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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

    client.register_entity_type(3, CentralDvcSwitch, async_add_entities)  # HwControl


class CentralDvcSwitch(SwitchEntity, CentralDvcEntity):
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
        if io["Kind"] == 3:
            self._attr_device_class = SwitchDeviceClass.OUTLET

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
