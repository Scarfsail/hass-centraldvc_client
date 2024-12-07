import json
import logging
import threading

from signalrcore.hub_connection_builder import HubConnectionBuilder

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .centraldvc_data_processor import CentralDvcDataProcessor

_LOGGER = logging.getLogger(__name__)


class CentralDvcClient:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.processor = CentralDvcDataProcessor(hass, entry, self.set_io)

        url = entry.data["url"]
        self.hub = (
            HubConnectionBuilder().with_url(url, options={"verify_ssl": False}).build()
        )

    async def start(self):
        await self.hass.async_add_executor_job(self.hub.start)
        send_callback_received = threading.Lock()

        def callback(response):
            self.process_initial_load(response)
            self.hub.on("iosChanged", self.process_iosChanged)

            send_callback_received.release()

        self.hub.send("GetAllIos", [], callback)

        if not send_callback_received.acquire(timeout=10):
            raise ValueError("CALLBACK NOT RECEIVED")

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
