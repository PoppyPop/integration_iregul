"""Base entity classes for IRegul integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import IRegulCoordinator


class IRegulEntity(CoordinatorEntity[IRegulCoordinator]):
    """Base entity for IRegul data with shared behavior."""

    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        item_index: int,
        item_key: str,
        unique_prefix: str,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._item_id = item_index
        self._item_key = item_key

        device_id = entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{device_id}_{unique_prefix}_{item_index}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=entry.title,
            manufacturer="IRegul",
            serial_number=device_id,
        )

    def _get_items(self) -> dict[int, object]:
        """Return the mapping of items for this entity type."""
        return getattr(self.coordinator.data, self._item_key)

    @property
    def available(self) -> bool:
        """Return if entity is available based on coordinator freshness and item presence."""
        items = self._get_items()
        return super().available and not self.coordinator.is_data_stale() and self._item_id in items

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.available:
            self.async_write_ha_state()
            return

        item = self._get_items()[self._item_id]
        self._update(item)
        self.async_write_ha_state()

    def _update(self, item: object) -> None:
        """Update entity attributes from the item.

        Must be implemented by subclasses.
        """
        raise NotImplementedError
