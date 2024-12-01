from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change

# from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the switch platform from a config entry."""
    name = entry.data["name"]
    linked_entity = entry.data["linked_entity"]

    async_add_entities([HwControl(name, linked_entity)])


class HwControl(SwitchEntity):
    """Representation of a HwControl entity."""

    def __init__(self, name: str, linked_entity: str) -> None:
        """Initialize the HwControl."""
        self._name = name
        self._linked_entity = linked_entity

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to Home Assistant."""
        # Track state changes for the linked switch
        async_track_state_change(
            self.hass, self._linked_entity, self._handle_linked_entity_change
        )

    async def _handle_linked_entity_change(self, entity_id, old_state, new_state):
        """Handle state changes for the linked switch."""
        # Notify Home Assistant of a state update
        self.schedule_update_ha_state()

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        state = self.hass.states.get(self._linked_entity)
        if state:
            return state.state == "on"
        return False

    def turn_on(self, **kwargs) -> None:
        """Turn on the switch."""
        domain = self.get_domain(self._linked_entity)
        self.hass.services.call(domain, "turn_on", {"entity_id": self._linked_entity})
        # self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        domain = self.get_domain(self._linked_entity)
        self.hass.services.call(domain, "turn_off", {"entity_id": self._linked_entity})
        # self._is_on = False
        self.schedule_update_ha_state()

    def get_domain(self, entity_id):
        """Get domain from entity ID."""
        return entity_id.split(".")[0]
