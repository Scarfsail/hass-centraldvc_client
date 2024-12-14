from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN  # Define DOMAIN in const.py


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    # Forward the entry setup to the switch platform
    # hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setup(entry, "select")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle unloading of a config entry."""
    # Remove platform setup
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "select")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
