from collections.abc import Callable

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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
        3,
        EntityDefinition(
            CentralDvcSwitch, async_add_entities, None, lambda io: io["Kind"] == 1
        ),
    )  # Generic

    processor.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcSwitch,
            async_add_entities,
            SwitchDeviceClass.OUTLET,
            lambda io: io["Kind"] == 3,
        ),
    )  # Power Plug

    processor.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcSwitch,
            async_add_entities,
            SwitchDeviceClass.OUTLET,
            lambda io: io["Kind"] == 4,
        ),
    )  # Sprinkler

    processor.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcSwitch,
            async_add_entities,
            SwitchDeviceClass.OUTLET,
            lambda io: io["Kind"] == 5,
        ),
    )  # Water Valve

    processor.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcSwitch,
            async_add_entities,
            SwitchDeviceClass.OUTLET,
            lambda io: io["Kind"] == 6,
        ),
    )  # Fan

    processor.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcSwitch,
            async_add_entities,
            SwitchDeviceClass.OUTLET,
            lambda io: io["Kind"] == 7,
        ),
    )  # Toshiba AC

    processor.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcSwitch,
            async_add_entities,
            SwitchDeviceClass.OUTLET,
            lambda io: io["Kind"] == 8,
        ),
    )  # Ev Charger

    processor.register_entity_type(
        3,
        EntityDefinition(
            CentralDvcSwitch,
            async_add_entities,
            SwitchDeviceClass.OUTLET,
            lambda io: io["Kind"] == 9,
        ),
    )  # Pool Heat pump


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
