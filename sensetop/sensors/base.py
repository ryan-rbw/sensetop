"""Base abstract sensor class for all sensor implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SensorStatus(Enum):
    """Enum representing the status of a sensor."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class SensorReading:
    """A single sensor reading with timestamp and metadata."""

    timestamp: datetime
    value: Any
    status: SensorStatus = SensorStatus.OK
    unit: str = ""
    raw_value: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return string representation of the reading."""
        return (
            f"SensorReading(timestamp={self.timestamp}, "
            f"value={self.value}{self.unit}, status={self.status.value})"
        )


class Sensor(ABC):
    """Abstract base class for all sensors.

    Provides a common interface for sensor data collection, validation,
    and status reporting.
    """

    def __init__(self, name: str, sensor_type: str) -> None:
        """Initialize sensor with name and type.

        Args:
            name: Human-readable sensor name (e.g., 'Temperature')
            sensor_type: Type of sensor (e.g., 'HTS221')
        """
        self.name = name
        self.sensor_type = sensor_type
        self._status = SensorStatus.OK
        self._last_error: Optional[Exception] = None
        self._reading_count = 0
        self._error_count = 0

    @property
    def status(self) -> SensorStatus:
        """Get current sensor status."""
        return self._status

    @property
    def last_error(self) -> Optional[Exception]:
        """Get the last error that occurred."""
        return self._last_error

    @property
    def reading_count(self) -> int:
        """Get total number of successful readings."""
        return self._reading_count

    @property
    def error_count(self) -> int:
        """Get total number of failed readings."""
        return self._error_count

    @property
    def error_rate(self) -> float:
        """Get the error rate as a percentage."""
        total = self._reading_count + self._error_count
        if total == 0:
            return 0.0
        return (self._error_count / total) * 100

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the sensor hardware connection.

        Should establish I2C connection, configure registers, etc.
        Raises: Exception if initialization fails.
        """

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the sensor and release resources."""

    @abstractmethod
    def read(self) -> SensorReading:
        """Read current sensor value.

        Returns:
            SensorReading: The current sensor reading with timestamp and status.

        Raises:
            Exception: If the read operation fails.
        """

    def _record_success(self) -> None:
        """Record a successful sensor read."""
        self._reading_count += 1
        self._status = SensorStatus.OK

    def _record_error(self, error: Exception) -> None:
        """Record a failed sensor read.

        Args:
            error: The exception that occurred during read.
        """
        self._error_count += 1
        self._last_error = error
        if self._error_rate > 50:
            self._status = SensorStatus.ERROR
        else:
            self._status = SensorStatus.WARNING

    @abstractmethod
    def get_specification(self) -> Dict[str, Any]:
        """Get sensor hardware specifications.

        Returns:
            Dict containing sensor specs like resolution, range, etc.
        """

    def validate_reading(self, value: Any) -> bool:
        """Validate if reading is within acceptable range.

        Args:
            value: The value to validate.

        Returns:
            bool: True if value is valid, False otherwise.
        """
        return True  # Default: all readings valid, override in subclasses

    def __repr__(self) -> str:
        """Return string representation of the sensor."""
        return (
            f"{self.__class__.__name__}(name={self.name}, "
            f"type={self.sensor_type}, status={self._status.value})"
        )
