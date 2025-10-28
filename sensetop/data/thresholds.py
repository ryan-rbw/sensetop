"""Threshold management and violation tracking."""

from copy import deepcopy
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, Tuple
import json


@dataclass
class SensorThreshold:
    """Threshold configuration for a single sensor."""

    sensor_name: str
    min_value: float = 0.0
    max_value: float = 100.0
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None
    enabled: bool = True

    def validate(self) -> None:
        """Validate threshold values.

        Raises:
            ValueError: If threshold values are invalid.
        """
        if self.min_value > self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) must be <= "
                f"max_value ({self.max_value})"
            )

        if self.critical_min is not None and self.critical_min > self.min_value:
            raise ValueError(
                f"critical_min ({self.critical_min}) must be <= "
                f"min_value ({self.min_value})"
            )

        if self.critical_max is not None and self.critical_max < self.max_value:
            raise ValueError(
                f"critical_max ({self.critical_max}) must be >= "
                f"max_value ({self.max_value})"
            )

    def check_value(self, value: float) -> Tuple[str, bool]:
        """Check if a value violates thresholds.

        Args:
            value: The sensor value to check.

        Returns:
            Tuple of (status, violated) where:
            - status: "ok", "warning", or "critical"
            - violated: True if any threshold exceeded
        """
        if not self.enabled:
            return ("ok", False)

        # Check critical thresholds first
        if self.critical_min is not None and value < self.critical_min:
            return ("critical", True)
        if self.critical_max is not None and value > self.critical_max:
            return ("critical", True)

        # Check warning thresholds
        if value < self.min_value or value > self.max_value:
            return ("warning", True)

        return ("ok", False)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SensorThreshold(sensor={self.sensor_name}, "
            f"min={self.min_value}, max={self.max_value})"
        )


class ThresholdManager:
    """Manage thresholds for multiple sensors."""

    # Default thresholds for common sensors
    DEFAULT_THRESHOLDS = {
        "temperature": SensorThreshold(
            sensor_name="temperature",
            min_value=0.0,
            max_value=50.0,
            critical_min=-40.0,
            critical_max=80.0,
        ),
        "humidity": SensorThreshold(
            sensor_name="humidity",
            min_value=30.0,
            max_value=70.0,
            critical_min=10.0,
            critical_max=90.0,
        ),
        "pressure": SensorThreshold(
            sensor_name="pressure",
            min_value=950.0,
            max_value=1050.0,
            critical_min=850.0,
            critical_max=1150.0,
        ),
        "cpu_temperature": SensorThreshold(
            sensor_name="cpu_temperature",
            min_value=20.0,
            max_value=60.0,
            critical_min=-10.0,
            critical_max=95.0,
        ),
        "memory_percent": SensorThreshold(
            sensor_name="memory_percent",
            min_value=0.0,
            max_value=75.0,
            critical_min=0.0,
            critical_max=95.0,
        ),
    }

    def __init__(self, config_file: Optional[str] = None) -> None:
        """Initialize threshold manager.

        Args:
            config_file: Path to threshold configuration file.
                        If None, uses ~/.sensetop/thresholds.json
        """
        if config_file is None:
            config_file = str(Path.home() / ".sensetop" / "thresholds.json")

        self.config_file = Path(config_file)
        self._thresholds: Dict[str, SensorThreshold] = {}

        # Load thresholds from file or use defaults
        self.load_from_file()

    def load_from_file(self) -> None:
        """Load thresholds from configuration file.

        If file doesn't exist, initializes with default thresholds.
        """
        self._thresholds = {}

        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for sensor_name, threshold_data in data.items():
                        threshold = SensorThreshold(**threshold_data)
                        threshold.validate()
                        self._thresholds[sensor_name] = threshold
            except (json.JSONDecodeError, ValueError) as e:
                # Fall back to defaults on error
                self._load_defaults()
        else:
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default thresholds."""
        self._thresholds = deepcopy(self.DEFAULT_THRESHOLDS)

    def save_to_file(self) -> None:
        """Save thresholds to configuration file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for sensor_name, threshold in self._thresholds.items():
            data[sensor_name] = asdict(threshold)

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def set_threshold(self, threshold: SensorThreshold) -> None:
        """Set threshold for a sensor.

        Args:
            threshold: SensorThreshold object.

        Raises:
            ValueError: If threshold values are invalid.
        """
        threshold.validate()
        self._thresholds[threshold.sensor_name] = threshold

    def get_threshold(self, sensor_name: str) -> Optional[SensorThreshold]:
        """Get threshold for a sensor.

        Args:
            sensor_name: Name of the sensor.

        Returns:
            SensorThreshold object or None if not found.
        """
        return self._thresholds.get(sensor_name)

    def check_value(self, sensor_name: str, value: float) -> Tuple[str, bool]:
        """Check if a sensor value violates thresholds.

        Args:
            sensor_name: Name of the sensor.
            value: The sensor value to check.

        Returns:
            Tuple of (status, violated).
        """
        threshold = self.get_threshold(sensor_name)
        if threshold is None:
            return ("ok", False)

        return threshold.check_value(value)

    def get_all_thresholds(self) -> Dict[str, SensorThreshold]:
        """Get all thresholds.

        Returns:
            Dictionary of sensor name to threshold.
        """
        return self._thresholds.copy()

    def reset_to_defaults(self) -> None:
        """Reset all thresholds to defaults."""
        self._load_defaults()

    def enable_sensor(self, sensor_name: str) -> None:
        """Enable threshold checking for a sensor."""
        threshold = self.get_threshold(sensor_name)
        if threshold:
            threshold.enabled = True

    def disable_sensor(self, sensor_name: str) -> None:
        """Disable threshold checking for a sensor."""
        threshold = self.get_threshold(sensor_name)
        if threshold:
            threshold.enabled = False

    def __repr__(self) -> str:
        """String representation."""
        return f"ThresholdManager(sensors={len(self._thresholds)})"
