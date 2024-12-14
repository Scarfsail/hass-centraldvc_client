import voluptuous as vol

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.event import async_track_state_change

TXT_ON = "ZAP"
TXT_OFF = "VYP"
TXT_AUTO = "AUTO"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the switch platform from a config entry."""
    name = entry.data["name"]
    linked_entity = entry.data["linked_entity"]
    entity = AutomationSwitch(name, linked_entity, entry)

    async_add_entities([entity])

    register_services()

    return True


def register_services():
    def set_value_when_auto(entity: AutomationSwitch, service_call):
        entity.set_value_when_auto(service_call.data["value"])

    def turn_on(entity: AutomationSwitch, service_call):
        entity.select_option(TXT_ON)

    def turn_off(entity: AutomationSwitch, service_call):
        entity.select_option(TXT_OFF)

    def set_auto(entity: AutomationSwitch, service_call):
        entity.select_option(TXT_AUTO)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "set_value_when_auto",
        {vol.Required("value"): cv.boolean},
        set_value_when_auto,
    )

    platform.async_register_entity_service(
        "turn_on",
        None,
        turn_on,
    )

    platform.async_register_entity_service(
        "turn_off",
        None,
        turn_off,
    )

    platform.async_register_entity_service(
        "set_auto",
        None,
        set_auto,
    )


class AutomationSwitch(SelectEntity):
    """Representation of a Automation Switch entity."""

    def __init__(self, name: str, linked_entity: str, entry) -> None:
        """Initialize the Automation Switch."""
        self._config_entry = entry
        self._name = name
        self._linked_entity = linked_entity
        self._is_auto_active = False
        self._value_when_auto = False

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
    def options(self):
        return [TXT_ON, TXT_OFF, TXT_AUTO]

    @property
    def current_option(self):
        if self._is_auto_active:
            return TXT_AUTO

        if self.is_on:
            return TXT_ON

        return TXT_OFF

    def select_option(self, option: str):
        if option == TXT_OFF:
            self.turn_off()
            self._is_auto_active = False
        if option == TXT_ON:
            self.turn_on()
            self._is_auto_active = False
        if option == TXT_AUTO:
            self._is_auto_active = True
            if self._value_when_auto:
                self.turn_on()
            else:
                self.turn_off()

    def set_value_when_auto(self, value):
        if self._value_when_auto == value:
            return

        self._value_when_auto = value
        if self._is_auto_active:
            if value:
                self.turn_on()
            else:
                self.turn_off()
        self.schedule_update_ha_state()

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        state = self.hass.states.get(self._linked_entity)
        if state:
            return state.state == "on"
        return False

    def turn_on(self) -> None:
        """Turn on the switch."""
        domain = self.get_domain(self._linked_entity)
        self.hass.services.call(domain, "turn_on", {"entity_id": self._linked_entity})
        # self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self) -> None:
        """Turn off the switch."""
        domain = self.get_domain(self._linked_entity)
        self.hass.services.call(domain, "turn_off", {"entity_id": self._linked_entity})
        # self._is_on = False
        self.schedule_update_ha_state()

    def get_domain(self, entity_id):
        """Get domain from entity ID."""
        return entity_id.split(".")[0]
