from http import HTTPStatus
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch, Mock, MagicMock

from aiohttp import RequestInfo, ClientSession
from spypointapi import SpypointApiInvalidCredentialsError
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.spypoint import DOMAIN


class ConfigFlowTest(IsolatedAsyncioTestCase):

    @patch('custom_components.spypoint.config_flow.SpypointApi')
    @patch('custom_components.spypoint.async_setup_entry')
    @patch('custom_components.spypoint.config_flow.async_create_clientsession')
    async def test_form_authentication_success(self, async_create_clientsession_constructor, async_setup_entry, api_constructor):
        api = self.spypoint_api_mock(api_constructor)
        async_create_clientsession = self.async_create_client_session_mock(async_create_clientsession_constructor)
        async_setup_entry.return_value = True
        hass = self.hass_setup()

        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER})

        # check form loaded
        self.assertEqual(result['type'], FlowResultType.FORM)
        self.assertIsNone(result['errors'])

        result = await hass.config_entries.flow.async_configure(result['flow_id'], {CONF_USERNAME: 'test-username', CONF_PASSWORD: 'test-password'})
        await hass.async_block_till_done()

        # check results
        self.assertEqual(result['version'], 1)
        self.assertEqual(result['type'], FlowResultType.CREATE_ENTRY)
        self.assertEqual(result['context'], {'source': 'user', 'unique_id': 'test-username'})
        self.assertEqual(result['title'], 'test-username')
        self.assertEqual(result['data'], {CONF_USERNAME: 'test-username', CONF_PASSWORD: 'test-password'})

        # api auth called
        api_constructor.assert_called_once_with('test-username', 'test-password', async_create_clientsession)
        api.async_authenticate.assert_called_once_with()

        # entry setup called
        async_setup_entry.assert_called_once()

    async def test_form_incomplete(self):
        hass = self.hass_setup()

        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(result['flow_id'], None)
        await hass.async_block_till_done()

        # show form
        self.assertEqual(result['type'], FlowResultType.FORM)

    @patch('custom_components.spypoint.config_flow.SpypointApi')
    @patch('custom_components.spypoint.config_flow.async_create_clientsession')
    async def test_form_authentication_error(self, async_create_clientsession_constructor, api_constructor):
        self.spypoint_api_mock(api_constructor, auth_success=False)
        self.async_create_client_session_mock(async_create_clientsession_constructor)
        hass = self.hass_setup()

        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(result['flow_id'], {CONF_USERNAME: 'test-username', CONF_PASSWORD: 'test-password'})
        await hass.async_block_till_done()

        # show form with error
        self.assertEqual(result['type'], FlowResultType.FORM)
        self.assertEqual(result['errors'], {"base": "invalid_auth"})

    @patch('custom_components.spypoint.config_flow.SpypointApi')
    @patch('custom_components.spypoint.async_setup_entry')
    @patch('custom_components.spypoint.config_flow.async_create_clientsession')
    async def test_form_re_authentication_success(self, async_create_clientsession_constructor, async_setup_entry, api_constructor):
        api = self.spypoint_api_mock(api_constructor)
        async_create_clientsession = self.async_create_client_session_mock(async_create_clientsession_constructor)
        async_setup_entry.return_value = True
        hass = self.hass_setup()

        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_REAUTH, 'entry_id': 'id'})
        result = await hass.config_entries.flow.async_configure(result['flow_id'], {CONF_USERNAME: 'test-username', CONF_PASSWORD: 'test-password-new'})
        await hass.async_block_till_done()

        api_constructor.assert_called_once_with('test-username', 'test-password-new', async_create_clientsession)
        api.async_authenticate.assert_called_once()

        self.assertEqual(result['type'], FlowResultType.CREATE_ENTRY)
        self.assertEqual(result['context'], {'source': 'reauth', 'entry_id': 'id', 'unique_id': 'test-username'})

    @staticmethod
    def hass_setup():
        hass = HomeAssistant(".")
        hass.data = {'components': {}, 'integrations': {}}
        hass.config_entries = ConfigEntries(hass, {})
        return hass

    @staticmethod
    def spypoint_api_mock(api_constructor, auth_success=True):
        api = AsyncMock()
        api_constructor.return_value = api

        api.async_authenticate = AsyncMock()
        if auth_success:
            api.async_authenticate.return_value = True
        else:
            api.async_authenticate.side_effect = SpypointApiInvalidCredentialsError(status=HTTPStatus.BAD_REQUEST, request_info=Mock(RequestInfo), history=())

        api.async_get_cameras = AsyncMock(return_value=[])

        return api

    @staticmethod
    def async_create_client_session_mock(async_create_clientsession_constructor):
        async_create_clientsession = MagicMock()
        async_create_clientsession_constructor.return_value = async_create_clientsession
        async_create_clientsession.return_value = AsyncMock(ClientSession)
        return async_create_clientsession
