from __future__ import annotations

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorEntity,
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
)
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription, \
    BinarySensorDeviceClass
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

MOTION_SENSOR_ENTITY_DESCRIPTION = BinarySensorEntityDescription(
    key="motion",
    device_class=BinarySensorDeviceClass.MOTION,
)

def to_data_update(parsed):
    _LOGGER.info("to_data_update=%s", parsed)

    if parsed is None:
        return None

    return PassiveBluetoothDataUpdate(
        devices={None: None},
        entity_descriptions={"motion": MOTION_SENSOR_ENTITY_DESCRIPTION},
        entity_data={"motion": parsed["motion"]},
        entity_names={"motion": "Motion Detected"},
    )

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    processor = PassiveBluetoothDataProcessor(to_data_update)

    _LOGGER.debug("Processor %s", processor)

    entry.async_on_unload(
        processor.async_add_entities_listener(MotionSensorEntity, async_add_entities)
    )
    entry.async_on_unload(coordinator.async_register_processor(processor))

class MotionSensorEntity(PassiveBluetoothProcessorEntity, BinarySensorEntity):
    entity_description: BinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        _LOGGER.info("is_on=%s", self.entity_key)
        return self.processor.entity_data.get(self.entity_key)