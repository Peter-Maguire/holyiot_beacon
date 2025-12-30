from __future__ import annotations
from typing import Any, Dict
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN

class BLEMotionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BLE Motion Sensor."""

    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        if user_input is not None:
            # Create entry with minimal data
            return self.async_create_entry(
                title=user_input["name"], data={"name": user_input["name"], "mac": user_input["mac"]}
            )

        # Show a simple form
        schema = vol.Schema(
            {
                vol.Required("name", default="HolyIoT Beacon"): str,
                vol.Required("mac"): str
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
