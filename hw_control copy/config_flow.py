import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class HwControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HwControl."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "name": user_input["name"],
                    "linked_entity": user_input["linked_entity"],
                },
            )

        # Dynamically get all valid entities
        entities = self._get_binary_control_entities()
        if not entities:
            return self.async_abort(reason="no_entities_found")

        # Create the dropdown schema
        data_schema = vol.Schema(
            {
                vol.Required("name", default="My HW Control"): str,
                vol.Required("linked_entity"): vol.In(
                    {entity: entity for entity in entities}
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=None,
        )

    @callback
    def _get_binary_control_entities(self):
        """Retrieve a list of entities that support turn_on and turn_off."""
        entities = []
        for entity in self.hass.states.async_all():
            domain = entity.entity_id.split(".")[0]
            # if domain in SUPPORTED_DOMAINS:
            # Check if the domain has turn_on and turn_off services
            if self._supports_binary_control(domain):
                entities.append(entity.entity_id)
        return entities

    @callback
    def _supports_binary_control(self, domain):
        """Check if the domain supports turn_on and turn_off services."""
        services = self.hass.services.async_services()
        return (
            domain in services
            and "turn_on" in services[domain]
            and "turn_off" in services[domain]
        )
