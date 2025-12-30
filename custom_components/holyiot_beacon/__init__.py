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
    """
    Parse BLE advertisement to detect motion state.
    """

    # Try manufacturer data first (device sends raw bytes)
    raw_bytes = None

    # homeassistant BLE API exposes service_info.manufacturer_data
    if service_info.manufacturer_data:
        for _, value in service_info.manufacturer_data.items():
            raw_bytes = value
            break

    if raw_bytes is None:
        return None

    if isinstance(raw_bytes, str):
        raw_bytes = bytes.fromhex(raw_bytes)

    # Last 4 bytes differentiate motion vs no motion
    # motion: 03 04 01 00
    # no motion: 03 06 00 00
    if len(raw_bytes) >= 4:
        last4 = raw_bytes[-4:]
        motion = (last4[0] == 0x03 and last4[1] == 0x04)
        return {"motion": motion}

    return None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BLE Motion Sensor integration entry."""

    # Address is optional; if you know the MAC you could store it
    address = entry.title

    coordinator = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=None,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=parse_motion,
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(coordinator.async_start())
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
