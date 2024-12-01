import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class HwControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HwControl."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Create a config entry
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "name": user_input["name"],
                    "linked_switch": user_input["linked_switch"],
                },
            )

        # Show the setup form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default="My HW Control"): str,
                    vol.Required("linked_switch"): str,
                }
            ),
        )
