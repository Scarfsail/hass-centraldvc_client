from abc import ABC, abstractmethod
from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import run_callback_threadsafe


class CentralDvcEntity(ABC, Entity):
    def __init__(
        self,
        id,
        config_entry: ConfigEntry,
        hass: HomeAssistant,
        io,
        set_io: Callable[[int, str], None],
        device_class: str | None = None,
    ):
        self._config_entry = config_entry
        self.hass = hass
        self.client_set_io = set_io

        if device_class:
            self._attr_device_class = device_class

        self.io = io
        self.io_id = io["Id"]
        self._id = id
        self._name = io["Title"]
        self._is_online = io["IsOnline"]
        self.io_changed(io)

    def update_from_io(self, io):
        self.io = self.io | io
        self._is_online = io["IsOnline"]
        self.io_changed(self.io)
        run_callback_threadsafe(self.hass.loop, self.async_write_ha_state)

    def set_is_offline(self):
        self._is_online = False
        run_callback_threadsafe(self.hass.loop, self.async_write_ha_state)

    @abstractmethod
    def io_changed(self, io): ...

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._id

    @property
    def available(self):
        """Return True if the sensor is available."""
        return self._is_online

    def set_io(self, value: str):
        self.client_set_io(self.io_id, value)
