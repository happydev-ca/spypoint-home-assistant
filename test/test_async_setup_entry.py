from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, AsyncMock, MagicMock

from aiohttp import ClientSession
from homeassistant.config_entries import ConfigEntry, ConfigEntries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from custom_components.spypoint import async_setup_entry, PLATFORMS, DOMAIN, SpypointCoordinator


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
# https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities
class AsyncSetupEntryTest(IsolatedAsyncioTestCase):

    @patch('custom_components.spypoint.SpypointApi')
    @patch('custom_components.spypoint.async_get_clientsession')
    async def test_creates_api_with_user_credentials(self, async_get_clientsession_constructor, api_constructor):
        self.spypoint_api_mock(api_constructor)
        async_get_clientsession = self.async_get_client_session_mock(async_get_clientsession_constructor)
        hass = self.hass_mock()
        entry = self.entry_mock(username='username', password='password')

        await async_setup_entry(hass=hass, entry=entry)

        api_constructor.assert_called_once_with('username', 'password', async_get_clientsession)

    @patch('custom_components.spypoint.SpypointApi')
    @patch('custom_components.spypoint.async_get_clientsession')
    async def test_forwards_entries(self, async_get_clientsession_constructor, api_constructor):
        self.spypoint_api_mock(api_constructor)
        self.async_get_client_session_mock(async_get_clientsession_constructor)
        hass = self.hass_mock()
        entry = self.entry_mock()

        await async_setup_entry(hass=hass, entry=entry)

        hass.config_entries.async_forward_entry_setups.assert_called_once_with(entry, PLATFORMS)

    @patch('custom_components.spypoint.SpypointApi')
    @patch('custom_components.spypoint.async_get_clientsession')
    async def test_starts_the_coordinator(self, async_get_clientsession_constructor, api_constructor):
        api = self.spypoint_api_mock(api_constructor)
        self.async_get_client_session_mock(async_get_clientsession_constructor)
        hass = self.hass_mock()
        entry = self.entry_mock(id='entry')

        await async_setup_entry(hass=hass, entry=entry)

        self.assertIsInstance(hass.data[DOMAIN]['entry'], SpypointCoordinator)
        api.async_get_cameras.assert_called_once()

    @patch('custom_components.spypoint.SpypointApi')
    @patch('custom_components.spypoint.async_get_clientsession')
    async def test_returns_true(self, async_get_clientsession_constructor, api_constructor):
        self.spypoint_api_mock(api_constructor)
        self.async_get_client_session_mock(async_get_clientsession_constructor)
        hass = self.hass_mock()
        entry = self.entry_mock()

        result = await async_setup_entry(hass=hass, entry=entry)
        self.assertTrue(result)

    @staticmethod
    def async_get_client_session_mock(async_get_clientsession_constructor):
        async_get_clientsession = MagicMock()
        async_get_clientsession_constructor.return_value = async_get_clientsession
        async_get_clientsession.return_value = AsyncMock(ClientSession)
        return async_get_clientsession

    @staticmethod
    def entry_mock(username='u', password='p', id='e'):
        entry = AsyncMock(ConfigEntry)
        entry.entry_id = id
        entry.data = {CONF_USERNAME: username, CONF_PASSWORD: password}
        return entry

    @staticmethod
    def hass_mock():
        hass = AsyncMock(HomeAssistant)
        hass.data = {}
        hass.config_entries = AsyncMock(ConfigEntries)
        return hass

    @staticmethod
    def spypoint_api_mock(api_constructor):
        api = AsyncMock()
        api_constructor.return_value = api
        async_get_cameras = AsyncMock(return_value=[])
        api.async_get_cameras = async_get_cameras
        return api
