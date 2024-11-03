from datetime import timedelta
from http import HTTPStatus
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from aiohttp import RequestInfo
from spypointapi import SpypointApi, Camera, SpypointApiInvalidCredentialsError, SpypointApiError
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.spypoint import SpypointCoordinator, DOMAIN


class TestSpypointCoordinator(IsolatedAsyncioTestCase):

    async def test_set_coordinator_name_to_domain(self):
        hass = Mock(HomeAssistant)
        api = Mock(SpypointApi)
        coordinator = SpypointCoordinator(hass=hass, api=api)

        self.assertEqual(coordinator.name, DOMAIN)

    async def test_refresh_data_every_60_seconds(self):
        hass = Mock(HomeAssistant)
        api = Mock(SpypointApi)
        coordinator = SpypointCoordinator(hass=hass, api=api)

        self.assertEqual(coordinator.update_interval, timedelta(seconds=60))

    async def test_get_cameras(self):
        hass = Mock(HomeAssistant)
        api = Mock(SpypointApi)
        coordinator = SpypointCoordinator(hass=hass, api=api)

        camera = Mock(Camera)
        camera.id = '123'
        api.async_get_cameras = AsyncMock(return_value=[camera])

        cameras = await coordinator._async_update_data()

        self.assertEqual(cameras, {"123": camera})

    async def test_triggers_a_reauth_on_invalid_credentials_error(self):
        hass = Mock(HomeAssistant)
        api = Mock(SpypointApi)
        coordinator = SpypointCoordinator(hass=hass, api=api)

        api.async_get_cameras.side_effect = SpypointApiInvalidCredentialsError(status=HTTPStatus.BAD_REQUEST, request_info=Mock(RequestInfo), history=())

        with self.assertRaises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    async def test_raise_on_other_api_error(self):
        hass = Mock(HomeAssistant)
        api = Mock(SpypointApi)
        coordinator = SpypointCoordinator(hass=hass, api=api)

        api.async_get_cameras.side_effect = SpypointApiError(status=HTTPStatus.BAD_REQUEST, request_info=Mock(RequestInfo), history=())

        with self.assertRaises(ConnectionError):
            await coordinator._async_update_data()
