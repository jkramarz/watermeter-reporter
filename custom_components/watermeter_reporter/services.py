"""Services for the Watermeter Reporter integration."""

from __future__ import annotations

import datetime
from typing import Any

import requests
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, SERVICE_SUBMIT_READING
from .submission import ReadingData, submit_reading

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("owner_name"): cv.string,
        vol.Required("address"): cv.string,
        vol.Required("primary_reading"): vol.Coerce(int),
        vol.Optional("meter_number"): cv.string,
        vol.Optional("secondary_reading"): vol.Coerce(int),
        vol.Optional("tertiary_reading"): vol.Coerce(int),
        vol.Optional("reading_date"): cv.date,
        vol.Optional("notes"): cv.string,
        vol.Optional("dry_run", default=False): cv.boolean,
    }
)


async def async_submit_reading(hass: HomeAssistant, call: Any) -> None:
    """Submit a reading through the Home Assistant service."""
    data = ReadingData(
        owner_name=call.data["owner_name"],
        address=call.data["address"],
        meter_number=call.data.get("meter_number", ""),
        primary_reading=call.data["primary_reading"],
        secondary_reading=call.data.get("secondary_reading"),
        tertiary_reading=call.data.get("tertiary_reading"),
        reading_date=call.data.get("reading_date", datetime.date.today()),
        notes=call.data.get("notes", ""),
        dry_run=call.data["dry_run"],
    )

    try:
        result = await hass.async_add_executor_job(submit_reading, data)
    except (ValueError, RuntimeError, requests.RequestException) as err:
        raise ServiceValidationError(str(err)) from err

    if not result["success"]:
        raise ServiceValidationError(result["message"])


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the Watermeter Reporter services."""
    hass.services.async_register(
        DOMAIN,
        SERVICE_SUBMIT_READING,
        async_submit_reading,
        schema=SERVICE_SCHEMA,
    )
