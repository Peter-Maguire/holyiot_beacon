from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothProcessorEntity,
    PassiveBluetoothDataUpdate,
)
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

def to_data_update(parsed):
    """Convert the parsed data into PassiveBluetoothDataUpdate."""
    if parsed is None:
        return None

    return PassiveBluetoothDataUpdate(
        devices={},
        entity_descriptions={},
        entity_data={(DOMAIN, "motion"): parsed["motion"]},
        entity_names={(DOMAIN, "motion"): "Motion Detected"},
    )

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    processor = PassiveBluetoothDataProcessor(to_data_update)

    entry.async_on_unload(
        processor.async_add_entities_listener(MotionSensorEntity, async_add_entities)
    )

    entry.async_on_unload(coordinator.async_register_processor(processor))

class MotionSensorEntity(PassiveBluetoothProcessorEntity, BinarySensorEntity):
    @property
    def is_on(self):
        return bool(self.processor.entity_data.get(self.entity_key))
