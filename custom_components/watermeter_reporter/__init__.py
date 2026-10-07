"""Watermeter Reporter custom integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .services import async_setup_services


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Watermeter Reporter service."""
    await async_setup_services(hass)
    return True
