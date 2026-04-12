"""Test configuration for the IRegul integration."""

from __future__ import annotations

from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def mock_iregul_client_calls() -> None:
    """Mock network calls from the aioiregul client in tests."""
    frame = SimpleNamespace(
        timestamp=datetime.now(UTC),
        measurements={},
        inputs={},
        outputs={},
        analog_sensors={},
    )

    with (
        patch(
            "custom_components.integration_iregul.coordinator.IRegulClient.check_auth",
            AsyncMock(return_value=True),
        ),
        patch(
            "custom_components.integration_iregul.coordinator.IRegulClient.get_data",
            AsyncMock(return_value=frame),
        ),
    ):
        yield
