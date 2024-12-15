import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, entity_registry as er

from .const import DOMAIN


class AutomationSwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Automation Switch."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Automation switch",
                data=user_input,
            )

        # Dynamically get all valid entities
        entities = get_binary_control_entities(self.hass)
        if not entities:
            return self.async_abort(reason="no_entities_found")

        # Create the dropdown schema
        data_schema = vol.Schema({vol.Required("entities"): cv.multi_select(entities)})

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=None,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow for reconfiguration."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update the config entry options
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        entities = get_binary_control_entities(self.hass)

        # Pre-select previously selected entities
        selected_entities = self.config_entry.data.get("entities", [])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "entities", default=selected_entities
                    ): cv.multi_select(entities)
                }
            ),
        )


def get_binary_control_entities(hass: HomeAssistant):
    """Retrieve a list of entities that support turn_on and turn_off."""
    entities = {}
    for entity in hass.states.async_all():
        domain = entity.entity_id.split(".")[0]
        # if domain in SUPPORTED_DOMAINS:
        # Check if the domain has turn_on and turn_off services
        if supports_binary_control(hass, domain):
            entities[entity.entity_id] = entity.name
    return entities


def supports_binary_control(hass: HomeAssistant, domain):
    """Check if the domain supports turn_on and turn_off services."""
    services = hass.services.async_services()
    return (
        domain in services
        and "turn_on" in services[domain]
        and "turn_off" in services[domain]
    )
