"""Watermeter Reporter custom integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .services import async_setup_services


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Watermeter Reporter service."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Watermeter Reporter service from a config entry."""
    hass.data.setdefault("watermeter_reporter", {})[entry.entry_id] = entry.data
    await async_setup_services(hass)
    return True
