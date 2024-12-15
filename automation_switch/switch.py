import voluptuous as vol

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    config_validation as cv,
    entity_platform,
    entity_registry,
)
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the switch platform from a config entry."""
    selected_entities = entry.data["entities"]

    # Get the entity registry
    entity_registry_obj = entity_registry.async_get(hass)

    # Remove entities that are no longer selected
    existing_entities = [
        entity
        for entity in entity_registry_obj.entities.values()
        if entity.config_entry_id == entry.entry_id
    ]
    selected_entities_automation = [
        "switch." + compose_automation_switch_id(entity_id)
        for entity_id in selected_entities
    ]
    for entity in existing_entities:
        if entity.entity_id not in selected_entities_automation:
            entity_registry_obj.async_remove(entity.entity_id)

    # Add new entities that are not yet created

    automation_switches = [
        AutomationSwitch(entity_id) for entity_id in selected_entities
    ]

    async_add_entities(automation_switches)

    register_services()


def register_services():
    def set_value_when_auto(entity: AutomationSwitch, service_call):
        entity.set_value_when_auto(service_call.data["value"])

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "set_value_when_auto",
        {vol.Required("value"): cv.boolean},
        set_value_when_auto,
    )


def compose_automation_switch_id(linked_entity_id: str):
    return linked_entity_id.replace(".", "_") + "_automation"


class AutomationSwitch(SwitchEntity, RestoreEntity):
    """Representation of a HwControl entity."""

    def __init__(self, linked_entity_id: str) -> None:
        """Initialize the HwControl."""
        self._id = compose_automation_switch_id(linked_entity_id)
        self._linked_entity_id = linked_entity_id
        self._value_when_auto = False
        self._is_on = False

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to Home Assistant."""
        # Track state changes for the linked switch
        async_track_state_change(
            self.hass, self._linked_entity_id, self._handle_linked_entity_change
        )

    async def _handle_linked_entity_change(self, entity_id, old_state, new_state):
        """Handle state changes for the linked switch."""
        # Notify Home Assistant of a state update
        self.schedule_update_ha_state()

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        state = self.hass.states.get(self._linked_entity_id)
        return self._id if state is None else state.name + " Automation"
        # return self._name

    @property
    def suggested_object_id(self):
        """Return the suggested object id."""
        return self._id

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._id

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        # state = self.hass.states.get(self._linked_entity)
        # if state:
        #    return state.state == "on"
        return self._is_on

    @property
    def available(self) -> bool:
        """Return if the switch is available."""
        return True

    #    linked_entity = self.hass.states.get(self._linked_entity_id)
    #    return linked_entity is not None and linked_entity.state != "unavailable"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        linked_entity = self.hass.states.get(self._linked_entity_id)
        linked_entity_state = linked_entity.state if linked_entity else None

        return {
            "value_when_auto": self._value_when_auto,
            "linked_entity_state": linked_entity_state,
            "linked_entity_id": self._linked_entity_id,
        }

    def turn_on(self, **kwargs) -> None:
        """Turn on the switch."""

        domain = self.get_domain(self._linked_entity_id)
        self.hass.services.call(
            domain,
            "turn_on" if self._value_when_auto else "turn_off",
            {"entity_id": self._linked_entity_id},
        )
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        # domain = self.get_domain(self._linked_entity)
        # self.hass.services.call(domain, "turn_off", {"entity_id": self._linked_entity})
        self._is_on = False

        self.schedule_update_ha_state()

    def set_value_when_auto(self, value):
        if self._value_when_auto == value:
            return

        self._value_when_auto = value
        domain = self.get_domain(self._linked_entity_id)

        if self.is_on:
            if value:
                self.hass.services.call(
                    domain, "turn_on", {"entity_id": self._linked_entity_id}
                )
            else:
                self.hass.services.call(
                    domain, "turn_off", {"entity_id": self._linked_entity_id}
                )

        self.schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Restore state when the entity is added to hass."""
        await super().async_added_to_hass()
        # Retrieve the previous state

        old_state = await self.async_get_last_state()
        if old_state and old_state.state == "on":
            self._is_on = True
        elif old_state and old_state.state == "off":
            self._is_on = False

    def get_domain(self, entity_id):
        """Get domain from entity ID."""
        return entity_id.split(".")[0]
