"""
Spypoint cameras
"""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from spypointapi import Camera

from . import SpypointCoordinator
from .const import DOMAIN, MANUFACTURER, LOGGER


async def async_setup_entry(hass, entry, async_add_devices) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for camera in coordinator.data.values():
        LOGGER.debug(camera)
        sensors.append(SignalSensor(coordinator, camera))
        sensors.append(TemperatureSensor(coordinator, camera))
        sensors.append(BatterySensor(coordinator, camera))
        sensors.append(BatteryTypeSensor(coordinator, camera))
        sensors.append(MemorySensor(coordinator, camera))
        sensors.append(OnlineSensor(coordinator, camera))
        sensors.append(LastUpdateSensor(coordinator, camera))
        sensors.append(NotificationsSensor(coordinator, camera))
        if camera.owner is not None:
            sensors.append(OwnerSensor(coordinator, camera))

    async_add_devices(sensors)


class SpypointCameraDevice(CoordinatorEntity):
    _attr_attribution = f'Data provided by {MANUFACTURER}'

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera, sensor_name: str) -> None:
        super().__init__(coordinator)
        device_name = f'{MANUFACTURER} {camera.name}'
        self._attr_name = f'{device_name} {sensor_name}'
        self._attr_unique_id = slugify(self._attr_name)
        self._camera = camera
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, camera.id)},
            manufacturer=MANUFACTURER,
            model=camera.model,
            sw_version=camera.camera_firmware,
            hw_version=camera.modem_firmware,
            name=device_name)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._camera = self.coordinator.data[self._camera.id]
        self.async_write_ha_state()


class SignalSensor(SpypointCameraDevice, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Cellular Signal Strength')

    @property
    def native_value(self):
        return self._camera.signal


class TemperatureSensor(SpypointCameraDevice, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Temperature')

    @property
    def native_value(self):
        return self._camera.temperature


class BatterySensor(SpypointCameraDevice, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Battery Level')

    @property
    def native_value(self):
        return self._camera.battery


class BatteryTypeSensor(SpypointCameraDevice, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Battery Type')

    @property
    def native_value(self):
        return self._camera.battery_type


class MemorySensor(SpypointCameraDevice, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'SD Card Usage')

    @property
    def native_value(self):
        return self._camera.memory


class LastUpdateSensor(SpypointCameraDevice, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Last Update')

    @property
    def native_value(self):
        return self._camera.last_update_time


class OnlineSensor(SpypointCameraDevice, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ['Online', 'Offline']

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Status')

    @property
    def native_value(self):
        if self._camera.is_online:
            return 'Online'
        return 'Offline'


class NotificationsSensor(SpypointCameraDevice, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Notifications')

    @property
    def native_value(self):
        if self._camera.notifications is None or len(self._camera.notifications) == 0:
            return "None"
        return ", ".join(self._camera.notifications)


class OwnerSensor(SpypointCameraDevice, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Owner')

    @property
    def native_value(self):
        return self._camera.owner