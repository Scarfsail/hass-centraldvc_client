from typing import Callable

from homeassistant.components.button import ButtonEntity
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

    client.register_entity_type(
        16, CentralDvcButton, async_add_entities
    )  # DigitalPulse


class CentralDvcButton(ButtonEntity, CentralDvcEntity):
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

    async def async_press(self) -> None:
        """Handle the button press."""
        self.set_io("1")

    def io_changed(self, io):
        """Update the sensor state and availability from the new IO data."""
