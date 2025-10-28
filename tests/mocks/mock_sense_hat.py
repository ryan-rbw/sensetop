"""Mock Sense HAT implementation for testing without hardware.

Provides a complete mock of the sense-hat library interface that can be used
in unit and integration tests without requiring actual Sense HAT hardware.
"""

import random
from typing import Any, Dict


class MockSenseHat:
    """Mock implementation of sense-hat SenseHat class.

    Provides the same interface as the real SenseHat but with simulated data.
    """

    def __init__(self) -> None:
        """Initialize mock Sense HAT."""
        self._closed = False

        # Initialize LED matrix (8x8 = 64 pixels)
        self._pixels = [0, 0, 0] * 64

        # Sensor state
        self._temperature = 22.5
        self._humidity = 45.0
        self._pressure = 1013.25

        # IMU state
        self._accel = {"x": 0, "y": 0, "z": 32767}  # ~1G in Z
        self._gyro = {"x": 0, "y": 0, "z": 0}
        self._compass = {"x": 20000, "y": 30000, "z": 40000}

    def close(self) -> None:
        """Close the Sense HAT connection."""
        self._closed = True

    # --- Temperature & Humidity Sensor (HTS221) ---

    def get_temperature(self) -> float:
        """Get temperature in Celsius.

        Returns:
            Temperature value with small random variation.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        # Add small random variation to simulate real sensor
        return self._temperature + random.gauss(0, 0.1)

    def get_humidity(self) -> float:
        """Get relative humidity in percent.

        Returns:
            Humidity value (0-100) with small random variation.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        # Clamp between 0 and 100
        return max(0, min(100, self._humidity + random.gauss(0, 0.5)))

    # --- Pressure Sensor (LPS25H) ---

    def get_pressure(self) -> float:
        """Get atmospheric pressure in hPa.

        Returns:
            Pressure value with small random variation.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        return self._pressure + random.gauss(0, 0.5)

    # --- Accelerometer (LSM9DS1) ---

    def get_accelerometer(self) -> Dict[str, float]:
        """Get accelerometer data in G-force.

        Returns:
            Dictionary with 'x', 'y', 'z' keys with acceleration values.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        raw = self.get_accelerometer_raw()
        # Convert raw to G-force (range: ±16G, resolution: 0.000732 G/LSB)
        resolution = 0.000732
        return {
            "x": raw["x"] * resolution,
            "y": raw["y"] * resolution,
            "z": raw["z"] * resolution,
        }

    def get_accelerometer_raw(self) -> Dict[str, int]:
        """Get raw accelerometer data.

        Returns:
            Dictionary with 'x', 'y', 'z' keys with raw integer values.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        # Add slight variation
        return {
            "x": self._accel["x"] + random.randint(-100, 100),
            "y": self._accel["y"] + random.randint(-100, 100),
            "z": self._accel["z"] + random.randint(-100, 100),
        }

    # --- Gyroscope (LSM9DS1) ---

    def get_gyroscope(self) -> Dict[str, float]:
        """Get gyroscope data in degrees per second.

        Returns:
            Dictionary with 'x', 'y', 'z' keys with rotation rate values.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        raw = self.get_gyroscope_raw()
        # Convert raw to deg/s (range: ±2000 deg/s, resolution: 0.07 deg/s/LSB)
        resolution = 0.07
        return {
            "x": raw["x"] * resolution,
            "y": raw["y"] * resolution,
            "z": raw["z"] * resolution,
        }

    def get_gyroscope_raw(self) -> Dict[str, int]:
        """Get raw gyroscope data.

        Returns:
            Dictionary with 'x', 'y', 'z' keys with raw integer values.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        # Add slight variation
        return {
            "x": self._gyro["x"] + random.randint(-50, 50),
            "y": self._gyro["y"] + random.randint(-50, 50),
            "z": self._gyro["z"] + random.randint(-50, 50),
        }

    # --- Magnetometer/Compass (LSM9DS1) ---

    def get_compass(self) -> Dict[str, float]:
        """Get magnetometer data in Gauss.

        Returns:
            Dictionary with 'x', 'y', 'z' keys with magnetic field values.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        raw = self.get_compass_raw()
        # Convert raw to Gauss (range: ±4G, resolution: 0.000014 G/LSB)
        resolution = 0.000014
        return {
            "x": raw["x"] * resolution,
            "y": raw["y"] * resolution,
            "z": raw["z"] * resolution,
        }

    def get_compass_raw(self) -> Dict[str, int]:
        """Get raw magnetometer data.

        Returns:
            Dictionary with 'x', 'y', 'z' keys with raw integer values.
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        # Add slight variation
        return {
            "x": self._compass["x"] + random.randint(-500, 500),
            "y": self._compass["y"] + random.randint(-500, 500),
            "z": self._compass["z"] + random.randint(-500, 500),
        }

    # --- Orientation (uses IMU data) ---

    def get_orientation(self) -> Dict[str, float]:
        """Get device orientation using IMU sensor fusion.

        Returns:
            Dictionary with 'pitch', 'roll', 'yaw' keys (in degrees).
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        # Return simulated orientation
        return {
            "pitch": random.gauss(0, 1),
            "roll": random.gauss(0, 1),
            "yaw": random.gauss(180, 5),
        }

    # --- LED Matrix ---

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """Set a single pixel on the LED matrix.

        Args:
            x: X coordinate (0-7)
            y: Y coordinate (0-7)
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        if not (0 <= x < 8 and 0 <= y < 8):
            raise ValueError(f"Invalid pixel coordinates: {x}, {y}")

        idx = (y * 8 + x) * 3
        self._pixels[idx] = r
        self._pixels[idx + 1] = g
        self._pixels[idx + 2] = b

    def clear(self) -> None:
        """Clear the LED matrix (turn off all pixels)."""
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        self._pixels = [0, 0, 0] * 64

    def show_message(self, text: str, scroll_speed: float = 0.1) -> None:
        """Display scrolling text on the LED matrix.

        Args:
            text: Text to display
            scroll_speed: Speed of scrolling (delay between frames in seconds)
        """
        if self._closed:
            raise RuntimeError("Sense HAT connection closed")
        # Mock implementation - just pretend to display
        pass

    # --- Control Methods ---

    def set_sensor_state(
        self,
        temperature: float = None,
        humidity: float = None,
        pressure: float = None,
    ) -> None:
        """Set mock sensor values for testing.

        Args:
            temperature: Temperature in Celsius
            humidity: Humidity in percent (0-100)
            pressure: Pressure in hPa
        """
        if temperature is not None:
            self._temperature = temperature
        if humidity is not None:
            self._humidity = max(0, min(100, humidity))
        if pressure is not None:
            self._pressure = pressure

    def set_imu_state(
        self,
        accel: Dict[str, int] = None,
        gyro: Dict[str, int] = None,
        compass: Dict[str, int] = None,
    ) -> None:
        """Set mock IMU values for testing.

        Args:
            accel: Accelerometer raw values
            gyro: Gyroscope raw values
            compass: Magnetometer raw values
        """
        if accel is not None:
            self._accel.update(accel)
        if gyro is not None:
            self._gyro.update(gyro)
        if compass is not None:
            self._compass.update(compass)
