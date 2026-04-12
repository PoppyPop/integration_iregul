"""Tests for the IRegul config flow."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from custom_components.integration_iregul.const import (
    API_VERSION_V1,
    API_VERSION_V2,
    CONF_API_VERSION,
    CONF_DEVICE_ID,
    CONF_DEVICE_PASSWORD,
    CONF_HOST,
    CONF_SERIAL_NUMBER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL_V2,
    DOMAIN,
)
from custom_components.integration_iregul.coordinator import IRegulCoordinator
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("enable_custom_integrations"),
]

CONF_USE_CUSTOM_HOST = "use_custom_host"


def _get_schema_default(result: dict[str, Any], field_name: str) -> Any:
    """Return the default value for a form field."""
    for key in result["data_schema"].schema:
        if key.schema == field_name:
            return key.default()

    raise AssertionError(f"Field {field_name} not found in schema")


async def test_full_user_flow(hass):
    """Test going through the full two-step config flow."""
    with patch(
        "custom_components.integration_iregul.config_flow.validate_input",
        AsyncMock(return_value={"title": "IRegul"}),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_API_VERSION: API_VERSION_V2,
                CONF_SERIAL_NUMBER: "SN123456",
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "credentials"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "super-secret", CONF_USE_CUSTOM_HOST: False},
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "IRegul"
        assert result["data"] == {
            CONF_API_VERSION: API_VERSION_V2,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "super-secret",
            CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL_V2,
        }


async def test_duplicate_abort(hass):
    """Test aborting the flow when the serial is already configured."""
    existing = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_VERSION: API_VERSION_V1,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "old-secret",
        },
        unique_id="SN123456",
    )
    existing.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_API_VERSION: API_VERSION_V1, CONF_SERIAL_NUMBER: "SN123456"},
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_validate_input_uses_default_host_when_not_configured(hass):
    """Test validation does not force a host when none is configured."""
    with patch.object(IRegulCoordinator, "create_client") as mock_create_client:
        mock_create_client.return_value.check_auth = AsyncMock(return_value=True)

        await __import__(
            "custom_components.integration_iregul.config_flow",
            fromlist=["validate_input"],
        ).validate_input(
            hass,
            {
                CONF_API_VERSION: API_VERSION_V2,
                CONF_DEVICE_ID: "SN123456",
                CONF_DEVICE_PASSWORD: "super-secret",
            },
        )

        assert mock_create_client.call_args.args[4] is None


async def test_validate_input_uses_custom_host_when_configured(hass):
    """Test validation passes configured host to client creation."""
    with patch.object(IRegulCoordinator, "create_client") as mock_create_client:
        mock_create_client.return_value.check_auth = AsyncMock(return_value=True)

        await __import__(
            "custom_components.integration_iregul.config_flow",
            fromlist=["validate_input"],
        ).validate_input(
            hass,
            {
                CONF_API_VERSION: API_VERSION_V2,
                CONF_DEVICE_ID: "SN123456",
                CONF_DEVICE_PASSWORD: "super-secret",
                CONF_HOST: "custom.iregul.local",
            },
        )

        assert mock_create_client.call_args.args[4] == "custom.iregul.local"


async def test_options_flow_updates_password(hass):
    """Test updating the password through the options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_VERSION: API_VERSION_V2,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "old-secret",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "new-secret",
            CONF_UPDATE_INTERVAL: 5,
            CONF_USE_CUSTOM_HOST: False,
            CONF_HOST: "",
        },
    )
    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_PASSWORD] == "new-secret"
    assert result["data"][CONF_UPDATE_INTERVAL] == 5
    assert entry.options[CONF_PASSWORD] == "new-secret"
    assert entry.data[CONF_DEVICE_PASSWORD] == "new-secret"


async def test_options_flow_sets_host(hass):
    """Test setting a custom host through the options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_VERSION: API_VERSION_V2,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "secret",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "secret",
            CONF_UPDATE_INTERVAL: 5,
            CONF_USE_CUSTOM_HOST: True,
            CONF_HOST: "custom.example.com",
        },
    )
    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_HOST] == "custom.example.com"


async def test_options_flow_clears_host(hass):
    """Test that an empty host clears it from entry data, restoring the library default."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_VERSION: API_VERSION_V2,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "secret",
            CONF_HOST: "custom.example.com",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "secret",
            CONF_UPDATE_INTERVAL: 5,
            CONF_USE_CUSTOM_HOST: False,
            CONF_HOST: "",
        },
    )
    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert CONF_HOST not in entry.data


async def test_options_flow_restores_saved_host_in_form(hass):
    """Test the options form restores the current host and checkbox state."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_VERSION: API_VERSION_V2,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "secret",
            CONF_HOST: "custom.example.com",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert _get_schema_default(result, CONF_USE_CUSTOM_HOST) is True
    assert _get_schema_default(result, CONF_HOST) == "custom.example.com"


async def test_options_flow_requires_host_when_enabled(hass):
    """Test enabling a custom host requires a non-empty value."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_VERSION: API_VERSION_V2,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "secret",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "secret",
            CONF_UPDATE_INTERVAL: 5,
            CONF_USE_CUSTOM_HOST: True,
            CONF_HOST: "   ",
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "host_required"}
