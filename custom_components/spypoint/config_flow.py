"""
Spypoint cameras config flow
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from spypointapi import SpypointApi, SpypointApiInvalidCredentialsError, SpypointApiError
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class SpypointConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(self, data: dict[str, Any] | None = None) -> FlowResult:
        if data is None:
            return self.async_show_form(step_id='user', data_schema=STEP_USER_DATA_SCHEMA)

        if self._reauth_entry is None:
            await self.async_set_unique_id(data[CONF_USERNAME])
            self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        try:
            spypoint_api = SpypointApi(data[CONF_USERNAME], data[CONF_PASSWORD], async_create_clientsession(self.hass))
            await spypoint_api.async_authenticate()

            if self._reauth_entry is None:
                return self.async_create_entry(title=data[CONF_USERNAME], data=data)
            else:
                self.hass.config_entries.async_update_entry(self._reauth_entry, data=data)
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        except SpypointApiInvalidCredentialsError:
            errors['base'] = 'invalid_auth'
        except SpypointApiError:
            errors['base'] = 'cannot_connect'
        except Exception:
            LOGGER.exception('Unexpected exception')
            errors['base'] = 'unknown'

        return self.async_show_form(step_id='user', data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

    async def async_step_reauth(self, data: dict[str, Any] | None = None) -> FlowResult:
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_user(data)
