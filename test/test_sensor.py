from datetime import datetime, timedelta, UTC
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify
from spypointapi import Camera

from custom_components.spypoint import DOMAIN
from custom_components.spypoint.const import MANUFACTURER
from custom_components.spypoint.sensor import async_setup_entry, SignalSensor, TemperatureSensor, BatterySensor, MemorySensor, LastUpdateSensor, OnlineSensor, NotificationsSensor


class TestSensorCreation(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        entry = Mock()
        entry.entry_id = 'id'
        self.coordinator = Mock(DataUpdateCoordinator)
        self.camera = Camera(id="id", name="Test", model="model",
                             modem_firmware="modem_firmware", camera_firmware="camera_firmware",
                             last_update_time=datetime.now().replace(tzinfo=UTC) - timedelta(hours=10, minutes=0, seconds=0),
                             signal=100, temperature=20, battery=50, memory=45)
        self.coordinator.data = {'123': self.camera}
        hass = Mock(HomeAssistant)
        hass.data = {DOMAIN: {entry.entry_id: self.coordinator}}

        async_add_devices = Mock()

        await async_setup_entry(hass, entry, async_add_devices)

        async_add_devices.assert_called_once()

        self.sensors = async_add_devices.call_args.args[0]

    async def test_add_sensors_on_setup(self):
        self.assertEqual(len(self.sensors), 7)

    def test_signal_sensor_created(self):
        self.assert_sensor_created(type=SignalSensor,
                                   name='Cellular Signal Strength',
                                   state_class=SensorStateClass.MEASUREMENT,
                                   entity_category=EntityCategory.DIAGNOSTIC,
                                   unit=PERCENTAGE,
                                   value=100)

    def test_temperature_sensor_created(self):
        self.assert_sensor_created(type=TemperatureSensor,
                                   name='Temperature',
                                   state_class=SensorStateClass.MEASUREMENT,
                                   device_class=SensorDeviceClass.TEMPERATURE,
                                   unit=UnitOfTemperature.CELSIUS,
                                   value=20)

    def test_battery_sensor_created(self):
        self.assert_sensor_created(type=BatterySensor,
                                   name='Battery Level',
                                   state_class=SensorStateClass.MEASUREMENT,
                                   device_class=SensorDeviceClass.BATTERY,
                                   entity_category=EntityCategory.DIAGNOSTIC,
                                   unit=PERCENTAGE,
                                   value=50)

    def test_memory_consumed_sensor_created(self):
        self.assert_sensor_created(type=MemorySensor,
                                   name='SD Card Usage',
                                   state_class=SensorStateClass.MEASUREMENT,
                                   entity_category=EntityCategory.DIAGNOSTIC,
                                   unit=PERCENTAGE,
                                   value=45)

    def test_last_update_sensor_created(self):
        self.assert_sensor_created(type=LastUpdateSensor,
                                   name='Last Update',
                                   device_class=SensorDeviceClass.TIMESTAMP,
                                   value=self.camera.last_update_time)

    def test_online_sensor_created(self):
        self.assert_sensor_created(type=OnlineSensor,
                                   name='Status',
                                   device_class=SensorDeviceClass.ENUM,
                                   options=['Online', 'Offline'],
                                   value='Online')

    def test_notifications_sensor_created(self):
        self.assert_sensor_created(type=NotificationsSensor,
                                   name='Notifications',
                                   entity_category=EntityCategory.DIAGNOSTIC,
                                   value='None')

    def assert_sensor_created(self, type, name, state_class=None, device_class=None, unit=None, precision=None, options=None, value=None, entity_category=None):
        sensor = next(s for s in self.sensors if isinstance(s, type))
        self.assertEqual(sensor.coordinator, self.coordinator)
        self.assertEqual(sensor._camera, self.camera)
        self.assertEqual(sensor.device_info, DeviceInfo(identifiers={(DOMAIN, self.camera.id)},
                                                        manufacturer=MANUFACTURER,
                                                        model=self.camera.model,
                                                        sw_version=self.camera.camera_firmware,
                                                        hw_version=self.camera.modem_firmware,
                                                        name='Spypoint Test'))
        if state_class is not None:
            self.assertEqual(sensor._attr_state_class, state_class)
        if device_class is not None:
            self.assertEqual(sensor._attr_device_class, device_class)
        if unit is not None:
            self.assertEqual(sensor._attr_native_unit_of_measurement, unit)
        if precision is not None:
            self.assertEqual(sensor._attr_suggested_display_precision, precision)
        if options is not None:
            self.assertEqual(sensor._attr_options, options)
        if entity_category is not None:
            self.assertEqual(sensor._attr_entity_category, entity_category)

        self.assertEqual(sensor._attr_name, f'Spypoint Test {name}')
        self.assertEqual(sensor._attr_unique_id, f'spypoint_test_{slugify(name)}')

        self.assertEqual(sensor.native_value, value)
