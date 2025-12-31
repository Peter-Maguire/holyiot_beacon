from __future__ import annotations

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorEntity,
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate, PassiveBluetoothEntityKey,
)
from homeassistant.components.bluetooth.passive_update_processor import DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription, \
    BinarySensorDeviceClass
from homeassistant.core import callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util
from .const import DOMAIN
import logging
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

COOLDOWN_SECONDS = 30

MOTION_SENSOR_ENTITY_DESCRIPTION = BinarySensorEntityDescription(
    key="motion",
    device_class=BinarySensorDeviceClass.MOTION,
)

def to_data_update(parsed):
    _LOGGER.info("to_data_update=%s", parsed)

    if parsed is None:
        return None

    entity_key = PassiveBluetoothEntityKey("motion", DOMAIN)

    return PassiveBluetoothDataUpdate(
        devices={DOMAIN: DeviceInfo(name="HolyIoT Beacon", model="HolyIoT Beacon", manufacturer="HolyIoT")},
        entity_descriptions={entity_key: MOTION_SENSOR_ENTITY_DESCRIPTION},
        entity_data={entity_key: parsed["motion"]},
        entity_names={entity_key: "Motion Detected"},
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._attr_is_on = None
        self._last_state_change = dt_util.utcnow() - timedelta(seconds=COOLDOWN_SECONDS)

    @property
    def is_on(self) -> bool | None:
        return self._attr_is_on

    @callback
    def _handle_processor_update(
        self, new_data: PassiveBluetoothDataUpdate | None
    ) -> None:
        """Handle updated data from the processor."""
        if new_data is None:
            self.async_write_ha_state()
            return

        new_state = self.processor.entity_data.get(self.entity_key)

        if new_state == self._attr_is_on:
            return

        now = dt_util.utcnow()
        if now - self._last_state_change < timedelta(seconds=COOLDOWN_SECONDS):
            _LOGGER.debug("Cooldown active, ignoring state change for %s", self.entity_key)
            return

        _LOGGER.info("State change for %s: %s -> %s", self.entity_key, self._attr_is_on, new_state)
        self._attr_is_on = new_state
        self._last_state_change = now
        self.async_write_ha_state()