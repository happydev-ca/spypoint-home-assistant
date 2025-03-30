from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from homeassistant.components.device_tracker import SourceType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from spypointapi import Camera, Coordinates

from custom_components.spypoint import DOMAIN
from custom_components.spypoint.device_tracker import async_setup_entry, SpypointCameraTracker


class TestDeviceTrackerCreation(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        entry = Mock()
        entry.entry_id = 'id'
        self.coordinator = Mock(DataUpdateCoordinator)
        self.camera = Camera(
            id="id",
            name="Test",
            model="model",
            modem_firmware="modem_firmware",
            camera_firmware="camera_firmware",
            last_update_time=datetime.now().astimezone(),
            coordinates=Coordinates(latitude=45.1234, longitude=-70.5678)
        )
        self.coordinator.data = {'123': self.camera}
        hass = Mock(HomeAssistant)
        hass.data = {DOMAIN: {entry.entry_id: self.coordinator}}

        self.async_add_devices = Mock()
        await async_setup_entry(hass, entry, self.async_add_devices)
        self.async_add_devices.assert_called_once()
        self.trackers = self.async_add_devices.call_args.args[0]

    async def test_add_tracker_on_setup(self):
        self.assertEqual(len(self.trackers), 1)

        tracker = self.trackers[0]
        self.assertIsInstance(tracker, SpypointCameraTracker)
        self.assertEqual(tracker.coordinator, self.coordinator)
        self.assertEqual(tracker._camera, self.camera)
        self.assertEqual(tracker.source_type, SourceType.GPS)
        self.assertEqual(tracker.latitude, 45.1234)
        self.assertEqual(tracker.longitude, -70.5678)
        self.assertEqual(tracker._attr_name, 'Spypoint Test Location')

    async def test_no_device_tracker_when_no_coordinates(self):
        self.camera.coordinates = None
        self.coordinator.data = {'123': self.camera}

        self.async_add_devices.reset_mock()

        entry = Mock()
        entry.entry_id = 'id'
        hass = Mock(HomeAssistant)
        hass.data = {DOMAIN: {entry.entry_id: self.coordinator}}

        await async_setup_entry(hass, entry, self.async_add_devices)

        self.async_add_devices.assert_called_once()
        trackers = self.async_add_devices.call_args.args[0]
        self.assertEqual(len(trackers), 0)
