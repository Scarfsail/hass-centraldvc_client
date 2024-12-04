import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .centraldvc_client import CentralDvcClient
from .const import DOMAIN
from .sensor import CentralDvcAnalogSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up CentralDvc from a config entry."""

    # hub_connection.on("iosChanged", lambda data: process_iosChanged(hass, data))

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {}
    client = CentralDvcClient(hass, entry)

    hass.data[DOMAIN][entry.entry_id]["client"] = client

    # Forward setup for the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    entry.async_on_unload(
        # only start after all platforms have had a chance to subscribe
        await client.start()
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    client.stop()
    return True
