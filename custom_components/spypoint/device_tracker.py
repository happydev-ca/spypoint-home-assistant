"""
Spypoint camera location tracker
"""
from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from spypointapi import Camera

from . import SpypointCoordinator
from .const import DOMAIN
from .entity import SpypointCameraEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    trackers = []
    for camera in coordinator.data.values():
        if camera.coordinates is not None:
            trackers.append(SpypointCameraTracker(coordinator, camera))

    async_add_entities(trackers)


class SpypointCameraTracker(SpypointCameraEntity, TrackerEntity):

    def __init__(self, coordinator: SpypointCoordinator, camera: Camera) -> None:
        super().__init__(coordinator, camera, 'Location')

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def latitude(self) -> float:
        return self._camera.coordinates.latitude

    @property
    def longitude(self) -> float:
        return self._camera.coordinates.longitude
