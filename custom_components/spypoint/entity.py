"""
Spypoint camera
"""
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from spypointapi import Camera

from . import SpypointCoordinator
from .const import DOMAIN, MANUFACTURER


class SpypointCameraEntity(CoordinatorEntity):
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
