"""System metrics sensor module.

Collects system-level metrics from the Raspberry Pi:
- CPU temperature from thermal zone
- Memory usage (total, used, available)
- System uptime
- CPU usage (if available)
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sensetop.sensors.base import Sensor, SensorReading, SensorStatus


@dataclass
class SystemMetrics:
    """Container for system metrics data."""

    cpu_temp: float  # Celsius
    memory_total: int  # Bytes
    memory_used: int  # Bytes
    memory_available: int  # Bytes
    uptime: timedelta
    cpu_count: int = 1

    @property
    def memory_percent(self) -> float:
        """Get memory usage as percentage."""
        if self.memory_total == 0:
            return 0.0
        return (self.memory_used / self.memory_total) * 100

    def __repr__(self) -> str:
        """String representation of system metrics."""
        return (
            f"SystemMetrics(cpu_temp={self.cpu_temp:.1f}°C, "
            f"memory={self.memory_percent:.1f}% "
            f"({self.memory_used // (1024 * 1024)}MB/"
            f"{self.memory_total // (1024 * 1024)}MB), "
            f"uptime={self.uptime})"
        )


class SystemSensor(Sensor):
    """System metrics sensor.

    Collects CPU temperature, memory usage, and uptime from Raspberry Pi.
    """

    # CPU temperature thresholds
    TEMP_MIN = 0.0  # Celsius
    TEMP_MAX = 100.0  # Celsius
    TEMP_WARNING = 80.0  # Celsius
    TEMP_CRITICAL = 95.0  # Celsius

    # Thermal zone path (works on Raspberry Pi OS)
    THERMAL_ZONE_PATH = "/sys/class/thermal/thermal_zone0/temp"

    def __init__(self, use_mock: bool = False) -> None:
        """Initialize system sensor.

        Args:
            use_mock: If True, use mock data instead of reading from system.
        """
        super().__init__(name="System Metrics", sensor_type="RaspberryPi System")
        self._use_mock = use_mock
        self._initialized = False
        self._cpu_count = self._get_cpu_count()

    def initialize(self) -> None:
        """Initialize system sensor.

        This sensor doesn't require hardware initialization, just validation.
        """
        if self._initialized:
            return

        try:
            if not self._use_mock:
                # Check if we can read thermal data
                if not os.path.exists(self.THERMAL_ZONE_PATH):
                    raise RuntimeError(
                        f"Thermal zone not found at {self.THERMAL_ZONE_PATH}. "
                        "Ensure this is running on a Raspberry Pi."
                    )

            self._initialized = True

        except Exception as e:
            self._record_error(e)
            raise

    def shutdown(self) -> None:
        """Shutdown system sensor (no cleanup needed)."""
        self._initialized = False

    def read(self) -> SensorReading:
        """Read current system metrics.

        Returns:
            SensorReading: SystemMetrics wrapped with timestamp.

        Raises:
            RuntimeError: If reading fails.
        """
        if not self._initialized:
            raise RuntimeError("System sensor not initialized")

        try:
            timestamp = datetime.now()

            if self._use_mock:
                metrics = self._read_mock()
            else:
                metrics = self._read_system()

            self._record_success()

            return SensorReading(
                timestamp=timestamp,
                value=metrics,
                status=SensorStatus.OK,
                unit="mixed",
                metadata={
                    "temperature_unit": "Celsius",
                    "memory_unit": "Bytes",
                    "uptime_unit": "seconds",
                },
            )

        except Exception as e:
            self._record_error(e)
            raise RuntimeError(f"Failed to read system metrics: {e}") from e

    def _read_system(self) -> SystemMetrics:
        """Read actual system metrics."""
        # Read CPU temperature
        cpu_temp = self._read_cpu_temperature()

        # Read memory info from /proc/meminfo
        memory_info = self._read_memory_info()

        # Read uptime from /proc/uptime
        uptime = self._read_uptime()

        return SystemMetrics(
            cpu_temp=cpu_temp,
            memory_total=memory_info["MemTotal"],
            memory_used=memory_info["MemTotal"] - memory_info["MemAvailable"],
            memory_available=memory_info["MemAvailable"],
            uptime=uptime,
            cpu_count=self._cpu_count,
        )

    def _read_mock(self) -> SystemMetrics:
        """Read mock system metrics for testing."""
        return SystemMetrics(
            cpu_temp=45.5,
            memory_total=4294967296,  # 4GB
            memory_used=1610612736,  # 1.5GB
            memory_available=2684354560,  # 2.5GB
            uptime=timedelta(hours=10, minutes=30),
            cpu_count=4,
        )

    def _read_cpu_temperature(self) -> float:
        """Read CPU temperature from thermal zone.

        Returns:
            Temperature in Celsius.

        Raises:
            RuntimeError: If temperature cannot be read.
        """
        try:
            with open(self.THERMAL_ZONE_PATH, "r", encoding="utf-8") as f:
                # Temperature is in millidegrees Celsius
                temp_millidegrees = int(f.read().strip())
                return temp_millidegrees / 1000.0
        except Exception as e:
            raise RuntimeError(f"Failed to read CPU temperature: {e}") from e

    @staticmethod
    def _read_memory_info() -> Dict[str, int]:
        """Read memory information from /proc/meminfo.

        Returns:
            Dictionary with memory information in bytes.

        Raises:
            RuntimeError: If meminfo cannot be read.
        """
        try:
            meminfo = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    key, value, *unit = line.split()
                    # Remove colon from key and convert value to bytes
                    key = key.rstrip(":")
                    value_int = int(value)
                    if unit and unit[0] == "kB":
                        value_int *= 1024  # Convert kB to bytes
                    meminfo[key] = value_int

            # Ensure required keys exist
            required_keys = ["MemTotal", "MemAvailable"]
            for key in required_keys:
                if key not in meminfo:
                    raise KeyError(f"Missing {key} in /proc/meminfo")

            return meminfo

        except Exception as e:
            raise RuntimeError(f"Failed to read memory info: {e}") from e

    @staticmethod
    def _read_uptime() -> timedelta:
        """Read system uptime from /proc/uptime.

        Returns:
            System uptime as timedelta.

        Raises:
            RuntimeError: If uptime cannot be read.
        """
        try:
            with open("/proc/uptime", "r", encoding="utf-8") as f:
                uptime_seconds = float(f.read().split()[0])
                return timedelta(seconds=uptime_seconds)
        except Exception as e:
            raise RuntimeError(f"Failed to read system uptime: {e}") from e

    @staticmethod
    def _get_cpu_count() -> int:
        """Get number of CPUs.

        Returns:
            Number of CPUs available.
        """
        try:
            # Try to read from /proc/cpuinfo
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                content = f.read()
                return len(re.findall(r"^processor\s*:", content, re.MULTILINE))
        except Exception:
            # Fallback to os.cpu_count()
            count = os.cpu_count()
            return count if count is not None else 1

    def get_specification(self) -> Dict[str, Any]:
        """Get system sensor specifications.

        Returns:
            Dictionary with sensor specifications.
        """
        return {
            "name": self.name,
            "type": self.sensor_type,
            "cpu_count": self._cpu_count,
            "temperature": {
                "range": f"{self.TEMP_MIN}°C to {self.TEMP_MAX}°C",
                "warning_threshold": f"{self.TEMP_WARNING}°C",
                "critical_threshold": f"{self.TEMP_CRITICAL}°C",
            },
            "data_sources": [
                "/sys/class/thermal/thermal_zone0/temp",
                "/proc/meminfo",
                "/proc/uptime",
                "/proc/cpuinfo",
            ],
        }

    def validate_reading(self, value: Any) -> bool:
        """Validate system metrics reading.

        Args:
            value: SystemMetrics object to validate.

        Returns:
            bool: True if all values are within acceptable ranges.
        """
        if not isinstance(value, SystemMetrics):
            return False

        # Check temperature range (allow margin)
        if value.cpu_temp < self.TEMP_MIN - 10 or value.cpu_temp > self.TEMP_MAX + 10:
            return False

        # Check memory values are sensible
        if (
            value.memory_total <= 0
            or value.memory_used < 0
            or value.memory_available < 0
        ):
            return False

        # Memory used should not exceed total
        if value.memory_used > value.memory_total:
            return False

        # Uptime should be positive
        if value.uptime < timedelta(0):
            return False

        return True
