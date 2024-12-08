import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class CentralDvcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CentralDvc."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL  # Updated for local service

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate URL if needed
            return self.async_create_entry(
                title=user_input["name"],
                data={"name": user_input["name"], "url": user_input["url"]},
            )

        data_schema = vol.Schema(
            {
                vol.Required("name", default="CentralDvc Client"): str,
                vol.Required(
                    "url",
                    default="http://192.168.0.44:9082/api/centralDvc/RealtimeHub/",
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=None
        )

    async def async_step_reauth(self, user_input=None):
        pass

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CentralDvcOptionsFlowHandler(config_entry)


class CentralDvcOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_show_form(step_id="init")
