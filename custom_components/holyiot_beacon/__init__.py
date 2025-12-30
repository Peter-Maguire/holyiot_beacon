import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR]



def parse_motion(service_info):
    raw_bytes = service_info.service_data["00005242-0000-1000-8000-00805f9b34fb"]

    if isinstance(raw_bytes, str):
        raw_bytes = bytes.fromhex(raw_bytes)

    if len(raw_bytes) < 4:
        return None

    last4 = raw_bytes[-4:]

    _LOGGER.info("last4=%s", last4)

    motion_detected = last4[1] == 0x04

    _LOGGER.info("Motion detected=%s", motion_detected)

    return {"motion": motion_detected}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BLE Motion Sensor integration entry."""

    coordinator = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=entry.data["mac"],
        mode=BluetoothScanningMode.PASSIVE,
        update_method=parse_motion,
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(coordinator.async_start())
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
