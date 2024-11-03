import asyncio
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from spypointapi import SpypointApi, Camera, SpypointApiInvalidCredentialsError, SpypointApiError

from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SpypointCoordinator(DataUpdateCoordinator):
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, api: SpypointApi) -> None:
        super().__init__(hass=hass, logger=LOGGER, name=DOMAIN, update_interval=timedelta(seconds=60))
        self.api = api

    async def _async_update_data(self) -> dict[str, Camera]:
        try:
            async with asyncio.timeout(10):
                cameras = await self.api.async_get_cameras()
                return {camera.id: camera for camera in cameras}
        except SpypointApiInvalidCredentialsError as error:
            raise ConfigEntryAuthFailed from error
        except SpypointApiError as error:
            raise ConnectionError from error
