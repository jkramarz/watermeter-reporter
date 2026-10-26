"""Config flow for Watermeter Reporter."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN


class WatermeterReporterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a configuration flow for Watermeter Reporter."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Create the single configuration entry."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Watermeter Reporter",
                data={
                    "owner_name": user_input["owner_name"],
                    "address": user_input["address"],
                    "meter_number": user_input["meter_number"],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("owner_name"): cv.string,
                    vol.Required("address"): cv.string,
                    vol.Required("meter_number"): cv.string,
                }
            ),
        )

    async def async_step_reconfigure(self, user_input=None, entry=None) -> FlowResult:
        """Handle a reconfiguration flow."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                entry,
                data={
                    **entry.data,
                    **user_input,
                },
            )
            return self.async_abort(reason="reconfiguration_complete")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(key, default=entry.data.get(key, "")): cv.string
                    for key in ["owner_name", "address", "meter_number"]
                }
            ),
            description_placeholders={"entry_title": entry.title},
        )
