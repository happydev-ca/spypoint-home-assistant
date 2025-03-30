"""
Spypoint camera sensors
"""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from spypointapi import Camera

from . import SpypointCoordinator
from .const import DOMAIN, LOGGER
from .entity import SpypointCameraEntity


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


class SignalSensor(SpypointCameraEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Cellular Signal Strength')

    @property
    def native_value(self):
        return self._camera.signal


class TemperatureSensor(SpypointCameraEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Temperature')

    @property
    def native_value(self):
        return self._camera.temperature


class BatterySensor(SpypointCameraEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Battery Level')

    @property
    def native_value(self):
        return self._camera.battery


class BatteryTypeSensor(SpypointCameraEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Battery Type')

    @property
    def native_value(self):
        return self._camera.battery_type


class MemorySensor(SpypointCameraEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'SD Card Usage')

    @property
    def native_value(self):
        return self._camera.memory


class LastUpdateSensor(SpypointCameraEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Last Update')

    @property
    def native_value(self):
        return self._camera.last_update_time


class OnlineSensor(SpypointCameraEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ['Online', 'Offline']

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Status')

    @property
    def native_value(self):
        if self._camera.is_online:
            return 'Online'
        return 'Offline'


class NotificationsSensor(SpypointCameraEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Notifications')

    @property
    def native_value(self):
        if self._camera.notifications is None or len(self._camera.notifications) == 0:
            return "None"
        return ", ".join(self._camera.notifications)


class OwnerSensor(SpypointCameraEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Owner')

    @property
    def native_value(self):
        return self._camera.owner