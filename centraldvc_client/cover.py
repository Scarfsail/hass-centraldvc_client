from collections.abc import Callable

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
)
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
    processor = hass.data[DOMAIN][entry.entry_id]["client"].processor

    processor.register_entity_type(
        8, EntityDefinition(CentralDvcGate, async_add_entities, CoverDeviceClass.GARAGE)
    )  # Gate


class CentralDvcGate(CoverEntity, CentralDvcEntity):
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
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

    @property
    def is_closed(self):
        """Return the state of the sensor."""
        return self._state == 0

    @property
    def is_closing(self):
        """Return the state of the sensor."""
        return self._state == 3

    @property
    def is_opening(self):
        """Return the state of the sensor."""
        return self._state == 4

    @property
    def current_cover_position(self):
        """Return the state of the sensor."""
        match self._state:
            case 0:  # Closed
                return 0
            case 1:  # OpenedPartially
                return 50
            case 2:  # OpenedFully
                return 100
            case 3:  # Closing
                return 50
            case 4:  # Opening
                return 50
            case _:
                return 100

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        self.set_io("OPEN")

    async def async_close_cover(self, **kwargs):
        """Open the cover."""
        self.set_io("CLOSE")

    async def async_stop_cover(self, **kwargs):
        """Open the cover."""
        self.set_io("STOP")

    def io_changed(self, io):
        """Update the sensor state and availability from the new IO data."""
        self._state = io["State"]
