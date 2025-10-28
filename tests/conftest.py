"""Pytest configuration and fixtures for SenseTop tests."""

import sys
from pathlib import Path

import pytest

# Add the parent directory to the path so we can import sensetop
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_sense_hat():
    """Provide a mock Sense HAT instance for testing.

    Returns:
        MockSenseHat: A mock Sense HAT object.
    """
    from tests.mocks.mock_sense_hat import MockSenseHat

    return MockSenseHat()


@pytest.fixture
def mock_imu_sensor():
    """Provide a mock IMU sensor for testing.

    Returns:
        IMUSensor: An IMU sensor in mock mode.
    """
    from sensetop.sensors.imu import IMUSensor

    sensor = IMUSensor(use_mock=True)
    sensor.initialize()
    yield sensor
    sensor.shutdown()


@pytest.fixture
def mock_environmental_sensor():
    """Provide a mock environmental sensor for testing.

    Returns:
        EnvironmentalSensor: An environmental sensor in mock mode.
    """
    from sensetop.sensors.environmental import EnvironmentalSensor

    sensor = EnvironmentalSensor(use_mock=True)
    sensor.initialize()
    yield sensor
    sensor.shutdown()


@pytest.fixture
def mock_system_sensor():
    """Provide a mock system sensor for testing.

    Returns:
        SystemSensor: A system sensor in mock mode.
    """
    from sensetop.sensors.system import SystemSensor

    sensor = SystemSensor(use_mock=True)
    sensor.initialize()
    yield sensor
    sensor.shutdown()
