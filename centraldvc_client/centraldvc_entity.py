from abc import ABC, abstractmethod

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import run_callback_threadsafe


class CentralDvcEntity(ABC, Entity):
    def __init__(self, id, config_entry, hass, io):
        self._config_entry = config_entry
        self.hass = hass

        self.io = io

        self._id = id
        self._name = io["Title"]
        self._state = io["Value"]
        self._is_online = io["IsOnline"]
        self._units = io["Units"]

    def update_from_io(self, io):
        self.io = self.io | io
        self.io_changed(self.io)
        run_callback_threadsafe(self.hass.loop, self.async_write_ha_state)

    @abstractmethod
    def io_changed(self, io): ...
