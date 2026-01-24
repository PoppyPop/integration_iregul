"""Tests for the IRegul config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from custom_components.integration_iregul.const import (
    API_VERSION_V1,
    API_VERSION_V2,
    CONF_API_VERSION,
    CONF_DEVICE_ID,
    CONF_DEVICE_PASSWORD,
    CONF_SERIAL_NUMBER,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
)
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("enable_custom_integrations"),
]


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
            {CONF_API_VERSION: API_VERSION_V2, CONF_SERIAL_NUMBER: "SN123456"},
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "credentials"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "super-secret"},
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "IRegul"
        assert result["data"] == {
            CONF_API_VERSION: API_VERSION_V2,
            CONF_DEVICE_ID: "SN123456",
            CONF_DEVICE_PASSWORD: "super-secret",
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
        {CONF_PASSWORD: "new-secret", CONF_UPDATE_INTERVAL: 5},
    )
    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_PASSWORD: "new-secret", CONF_UPDATE_INTERVAL: 5}
    assert entry.options[CONF_PASSWORD] == "new-secret"
    assert entry.data[CONF_DEVICE_PASSWORD] == "new-secret"
