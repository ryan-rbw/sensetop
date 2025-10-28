"""Environmental sensor module.

Handles temperature, humidity, and pressure sensor data collection:
- HTS221: Temperature and humidity sensor
- LPS25H: Pressure sensor
"""

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from sensetop.sensors.base import Sensor, SensorReading, SensorStatus


@dataclass
class EnvironmentalData:
    """Container for environmental measurement data."""

    temperature: float  # Celsius
    humidity: float  # Relative humidity percentage (0-100)
    pressure: float  # Hectopascals (hPa)

    # Optional derived metrics
    dew_point: float = 0.0  # Celsius
    altitude: float = 0.0  # Meters (derived from pressure)

    def __repr__(self) -> str:
        """String representation of environmental data."""
        return (
            f"EnvironmentalData(temp={self.temperature:.1f}°C, "
            f"humidity={self.humidity:.1f}%, pressure={self.pressure:.1f}hPa, "
            f"dew_point={self.dew_point:.1f}°C, altitude={self.altitude:.1f}m)"
        )


class EnvironmentalSensor(Sensor):
    """Environmental sensor combining temperature, humidity, and pressure.

    Uses HTS221 for temperature/humidity and LPS25H for pressure.
    """

    # Temperature sensor specifications (HTS221)
    TEMP_MIN = -40.0
    TEMP_MAX = 120.0
    TEMP_RESOLUTION = 0.02  # Celsius per LSB

    # Humidity sensor specifications (HTS221)
    HUMIDITY_MIN = 0.0
    HUMIDITY_MAX = 100.0
    HUMIDITY_RESOLUTION = 0.004  # RH% per LSB

    # Pressure sensor specifications (LPS25H)
    PRESSURE_MIN = 260.0  # hPa
    PRESSURE_MAX = 1260.0  # hPa
    PRESSURE_RESOLUTION = 0.24  # Pa per LSB = 0.0024 hPa per LSB

    # Sea level pressure for altitude calculation
    SEA_LEVEL_PRESSURE = 1013.25  # hPa

    def __init__(self, use_mock: bool = False) -> None:
        """Initialize environmental sensor.

        Args:
            use_mock: If True, use mock data instead of real hardware.
        """
        super().__init__(name="Environmental", sensor_type="HTS221/LPS25H")
        self._use_mock = use_mock
        self._sense_hat: Optional[Any] = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize I2C connection to environmental sensors.

        Raises:
            RuntimeError: If sensor initialization fails.
        """
        if self._initialized:
            return

        try:
            if self._use_mock:
                # Mock mode - no actual hardware needed
                self._initialized = True
                return

            # Try to import and initialize real sense-hat
            try:
                from sense_hat import SenseHat

                self._sense_hat = SenseHat()
                # Verify sensors are accessible
                _ = self._sense_hat.get_temperature()
                _ = self._sense_hat.get_humidity()
                _ = self._sense_hat.get_pressure()
                self._initialized = True
            except ImportError:
                raise RuntimeError(
                    "sense-hat library not installed. "
                    "Install with: pip install sense-hat"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize environmental sensors: {e}")

        except Exception as e:
            self._record_error(e)
            raise

    def shutdown(self) -> None:
        """Shutdown environmental sensors and release resources."""
        if self._sense_hat is not None:
            try:
                self._sense_hat.close()
            except Exception:
                pass  # Ignore errors during shutdown
        self._initialized = False

    def read(self) -> SensorReading:
        """Read current environmental data.

        Returns:
            SensorReading: EnvironmentalData wrapped with timestamp.

        Raises:
            RuntimeError: If reading fails.
        """
        if not self._initialized:
            raise RuntimeError("Environmental sensor not initialized")

        try:
            timestamp = datetime.now()

            if self._use_mock:
                env_data = self._read_mock()
            else:
                env_data = self._read_hardware()

            self._record_success()

            return SensorReading(
                timestamp=timestamp,
                value=env_data,
                status=SensorStatus.OK,
                unit="mixed",
                metadata={
                    "temperature_unit": "Celsius",
                    "humidity_unit": "percent",
                    "pressure_unit": "hPa",
                    "altitude_unit": "meters",
                },
            )

        except Exception as e:
            self._record_error(e)
            raise RuntimeError(f"Failed to read environmental data: {e}") from e

    def _read_hardware(self) -> EnvironmentalData:
        """Read from actual hardware."""
        if self._sense_hat is None:
            raise RuntimeError("Environmental sensor not initialized")

        # Read temperature (Celsius)
        temperature = self._sense_hat.get_temperature()

        # Read humidity (0-100%)
        humidity = self._sense_hat.get_humidity()

        # Read pressure (hPa)
        pressure = self._sense_hat.get_pressure()

        # Calculate derived metrics
        dew_point = self._calculate_dew_point(temperature, humidity)
        altitude = self._calculate_altitude(pressure)

        return EnvironmentalData(
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            dew_point=dew_point,
            altitude=altitude,
        )

    def _read_mock(self) -> EnvironmentalData:
        """Read mock environmental data for testing."""
        return EnvironmentalData(
            temperature=22.5,
            humidity=45.0,
            pressure=1013.25,
            dew_point=11.5,
            altitude=0.0,
        )

    @staticmethod
    def _calculate_dew_point(temperature: float, humidity: float) -> float:
        """Calculate dew point from temperature and humidity.

        Uses the Magnus approximation formula.

        Args:
            temperature: Temperature in Celsius.
            humidity: Relative humidity as percentage (0-100).

        Returns:
            Dew point in Celsius.
        """
        if humidity <= 0:
            return temperature

        # Magnus constants
        a = 17.27
        b = 237.7

        # Intermediate calculation
        alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)

        # Dew point calculation
        dew_point = (b * alpha) / (a - alpha)

        return dew_point

    def _calculate_altitude(self, pressure: float) -> float:
        """Calculate altitude from atmospheric pressure.

        Uses the barometric formula assuming sea level pressure of 1013.25 hPa.

        Args:
            pressure: Atmospheric pressure in hPa.

        Returns:
            Altitude in meters.
        """
        if pressure <= 0:
            return 0.0

        # Barometric formula
        altitude = 44330 * (
            1.0 - math.pow(pressure / self.SEA_LEVEL_PRESSURE, 1.0 / 5.255)
        )

        return altitude

    def get_specification(self) -> Dict[str, Any]:
        """Get environmental sensor hardware specifications.

        Returns:
            Dictionary with sensor specifications.
        """
        return {
            "name": self.name,
            "type": self.sensor_type,
            "temperature": {
                "range": f"{self.TEMP_MIN}°C to {self.TEMP_MAX}°C",
                "resolution": f"{self.TEMP_RESOLUTION}°C/LSB",
            },
            "humidity": {
                "range": f"{self.HUMIDITY_MIN}% to {self.HUMIDITY_MAX}%",
                "resolution": f"{self.HUMIDITY_RESOLUTION}%/LSB",
            },
            "pressure": {
                "range": f"{self.PRESSURE_MIN}hPa to {self.PRESSURE_MAX}hPa",
                "resolution": f"{self.PRESSURE_RESOLUTION:.4f}hPa/LSB",
            },
        }

    def validate_reading(self, value: Any) -> bool:
        """Validate environmental reading.

        Args:
            value: EnvironmentalData object to validate.

        Returns:
            bool: True if all values are within acceptable ranges.
        """
        if not isinstance(value, EnvironmentalData):
            return False

        # Check temperature range (allow some margin for safety)
        if value.temperature < self.TEMP_MIN - 10 or value.temperature > self.TEMP_MAX + 10:
            return False

        # Check humidity range
        if value.humidity < self.HUMIDITY_MIN - 5 or value.humidity > self.HUMIDITY_MAX + 5:
            return False

        # Check pressure range
        if value.pressure < self.PRESSURE_MIN - 100 or value.pressure > self.PRESSURE_MAX + 100:
            return False

        # Dew point should be less than or equal to temperature
        if value.dew_point > value.temperature + 1:
            return False

        return True
