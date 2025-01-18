from homeassistant.helpers.entity_platform import AddEntitiesCallback
from collections.abc import Callable
from .centraldvc_entity import CentralDvcEntity


class EntityDefinition:
    def __init__(
        self,
        entity_class: type[CentralDvcEntity],
        async_add_entities: AddEntitiesCallback,
        device_class: str | None = None,
        selector: Callable[[dict], bool] | None = None,
    ):
        self.entity_class = entity_class
        self.async_add_entities = async_add_entities
        self.device_class = device_class
        self.selector = selector
