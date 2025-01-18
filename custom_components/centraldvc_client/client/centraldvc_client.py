import json
import logging
import threading
import time

from signalrcore.hub_connection_builder import HubConnectionBuilder

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .centraldvc_data_processor import CentralDvcDataProcessor

_LOGGER = logging.getLogger(__name__)


class CentralDvcClient:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.reconnect_interval = 5

        self.hass = hass
        self.entry = entry
        self.processor = CentralDvcDataProcessor(hass, entry, self.set_io)

        url = entry.data["url"]
        self.hub = (
            HubConnectionBuilder().with_url(url, options={"verify_ssl": False}).build()
        )
        self.hub.on("iosChanged", self.process_iosChanged)

        self.hub.on_open(self.on_open)
        self.hub.on_close(self.on_close)
        self.hub.on_error(self.on_error)

    def stop(self):
        self.hub.stop()

    def process_initial_load(self, response):
        data = json.loads(response.result)
        self.processor.process_data_update(data)

    def process_iosChanged(self, response):
        data = json.loads(response[0])
        self.processor.process_data_update(data)

    def set_io(self, io_id: int, value: str) -> None:
        self.hub.send("SetIo", [{"IoId": io_id, "Value": value, "Answers": []}])

    def connect(self):
        """Attempt to connect to the SignalR server from HASS thread."""
        self.hass.add_job(self.start)

    def start(self):
        """Attempt to start to the SignalR server."""
        try:
            _LOGGER.info("SignalR is starting ...")
            self.hub.start()
        except Exception as ex:
            _LOGGER.error(f"Failed to connect to SignalR: {ex}")
            self.schedule_reconnect()

    def schedule_reconnect(self):
        """Schedule reconnection attempts."""
        self.hub.stop()
        self.processor.set_all_entities_offline()

        _LOGGER.warning(f"Reconnecting in {self.reconnect_interval} seconds...")

        time.sleep(self.reconnect_interval)
        self.start()

    def on_open(self):
        """Handle connection established."""
        _LOGGER.info("SignalR connection established.")

        send_callback_received = threading.Lock()

        def callback(response):
            self.process_initial_load(response)
            send_callback_received.release()

        self.hub.send("GetAllIos", [], callback)

        if not send_callback_received.acquire(timeout=10):
            raise ValueError("CALLBACK NOT RECEIVED")

    def on_close(self):
        """Handle connection closed."""
        _LOGGER.warning("SignalR connection closed. Scheduling reconnect...")
        self.schedule_reconnect()

    def on_error(self, error):
        """Handle connection error."""
        _LOGGER.error(f"SignalR connection error: {error}. Scheduling reconnect...")
        self.schedule_reconnect()
