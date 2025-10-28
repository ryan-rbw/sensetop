"""IMU (Inertial Measurement Unit) sensor module.

Handles 9-DOF IMU data collection from the LSM9DS1 chip:
- 3-axis accelerometer
- 3-axis gyroscope
- 3-axis magnetometer
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from sensetop.sensors.base import Sensor, SensorReading, SensorStatus


@dataclass
class IMUData:
    """Container for complete IMU measurement data."""

    # Accelerometer data (G-force)
    accel_x: float
    accel_y: float
    accel_z: float

    # Gyroscope data (degrees per second)
    gyro_x: float
    gyro_y: float
    gyro_z: float

    # Magnetometer data (Gauss)
    mag_x: float
    mag_y: float
    mag_z: float

    # Calculated orientation angles
    pitch: float = 0.0  # Rotation around X-axis
    roll: float = 0.0  # Rotation around Y-axis
    yaw: float = 0.0  # Rotation around Z-axis

    def __repr__(self) -> str:
        """String representation of IMU data."""
        return (
            f"IMUData(accel=({self.accel_x:.2f}, {self.accel_y:.2f}, "
            f"{self.accel_z:.2f})G, gyro=({self.gyro_x:.2f}, {self.gyro_y:.2f}, "
            f"{self.gyro_z:.2f})°/s, mag=({self.mag_x:.2f}, {self.mag_y:.2f}, "
            f"{self.mag_z:.2f})Gs, angles=({self.pitch:.1f}°, {self.roll:.1f}°, "
            f"{self.yaw:.1f}°))"
        )


class IMUSensor(Sensor):
    """9-DOF IMU sensor (LSM9DS1).

    Provides access to accelerometer, gyroscope, and magnetometer data.
    """

    # Hardware specifications
    ACCEL_RANGE = 16  # +/- 16G
    GYRO_RANGE = 2000  # +/- 2000 deg/s
    MAG_RANGE = 4  # +/- 4 Gauss

    ACCEL_RESOLUTION = 0.000732  # G per LSB (for 16G range)
    GYRO_RESOLUTION = 0.07  # deg/s per LSB (for 2000 deg/s range)
    MAG_RESOLUTION = 0.000014  # Gauss per LSB

    def __init__(self, use_mock: bool = False) -> None:
        """Initialize IMU sensor.

        Args:
            use_mock: If True, use mock data instead of real hardware.
        """
        super().__init__(name="IMU 9-DOF", sensor_type="LSM9DS1")
        self._use_mock = use_mock
        self._sense_hat_imu: Optional[Any] = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize I2C connection to IMU sensor.

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

            # Try to import and initialize real sense-hat IMU
            try:
                from sense_hat import SenseHat

                self._sense_hat_imu = SenseHat()
                # Verify IMU is accessible by reading once
                _ = self._sense_hat_imu.get_accelerometer_raw()
                self._initialized = True
            except ImportError:
                raise RuntimeError(
                    "sense-hat library not installed. " "Install with: pip install sense-hat"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize IMU: {e}")

        except Exception as e:
            self._record_error(e)
            raise

    def shutdown(self) -> None:
        """Shutdown IMU sensor and release resources."""
        if self._sense_hat_imu is not None:
            try:
                self._sense_hat_imu.close()
            except Exception:
                pass  # Ignore errors during shutdown
        self._initialized = False

    def read(self) -> SensorReading:
        """Read current IMU data.

        Returns:
            SensorReading: IMUData wrapped in SensorReading with timestamp.

        Raises:
            RuntimeError: If reading fails.
        """
        if not self._initialized:
            raise RuntimeError("IMU sensor not initialized")

        try:
            timestamp = datetime.now()

            if self._use_mock:
                imu_data = self._read_mock()
            else:
                imu_data = self._read_hardware()

            self._record_success()

            return SensorReading(
                timestamp=timestamp,
                value=imu_data,
                status=SensorStatus.OK,
                unit="mixed",
                metadata={
                    "accel_unit": "G",
                    "gyro_unit": "deg/s",
                    "mag_unit": "Gauss",
                },
            )

        except Exception as e:
            self._record_error(e)
            raise RuntimeError(f"Failed to read IMU: {e}") from e

    def _read_hardware(self) -> IMUData:
        """Read from actual hardware."""
        if self._sense_hat_imu is None:
            raise RuntimeError("IMU not initialized")

        # Read accelerometer (in Gs)
        accel_raw = self._sense_hat_imu.get_accelerometer_raw()
        accel_x = accel_raw["x"] * self.ACCEL_RESOLUTION
        accel_y = accel_raw["y"] * self.ACCEL_RESOLUTION
        accel_z = accel_raw["z"] * self.ACCEL_RESOLUTION

        # Read gyroscope (in deg/s)
        gyro_raw = self._sense_hat_imu.get_gyroscope_raw()
        gyro_x = gyro_raw["x"] * self.GYRO_RESOLUTION
        gyro_y = gyro_raw["y"] * self.GYRO_RESOLUTION
        gyro_z = gyro_raw["z"] * self.GYRO_RESOLUTION

        # Read magnetometer (in Gauss)
        mag_raw = self._sense_hat_imu.get_compass_raw()
        mag_x = mag_raw["x"] * self.MAG_RESOLUTION
        mag_y = mag_raw["y"] * self.MAG_RESOLUTION
        mag_z = mag_raw["z"] * self.MAG_RESOLUTION

        # Calculate orientation angles from accelerometer
        pitch, roll, yaw = self._calculate_orientation(accel_x, accel_y, accel_z)

        return IMUData(
            accel_x=accel_x,
            accel_y=accel_y,
            accel_z=accel_z,
            gyro_x=gyro_x,
            gyro_y=gyro_y,
            gyro_z=gyro_z,
            mag_x=mag_x,
            mag_y=mag_y,
            mag_z=mag_z,
            pitch=pitch,
            roll=roll,
            yaw=yaw,
        )

    def _read_mock(self) -> IMUData:
        """Read mock IMU data for testing."""
        return IMUData(
            accel_x=0.0,
            accel_y=0.0,
            accel_z=1.0,  # 1G in Z direction (normal gravity)
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
            mag_x=20.0,
            mag_y=30.0,
            mag_z=40.0,
            pitch=0.0,
            roll=0.0,
            yaw=0.0,
        )

    @staticmethod
    def _calculate_orientation(
        accel_x: float, accel_y: float, accel_z: float
    ) -> tuple[float, float, float]:
        """Calculate orientation angles from accelerometer data.

        Uses simple arctan-based calculation (not a full IMU fusion algorithm).

        Args:
            accel_x: Acceleration in X direction (G).
            accel_y: Acceleration in Y direction (G).
            accel_z: Acceleration in Z direction (G).

        Returns:
            Tuple of (pitch, roll, yaw) angles in degrees.
        """
        import math

        # Calculate pitch and roll from accelerometer
        pitch = math.atan2(accel_y, accel_z) * 180 / math.pi
        roll = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)) * 180 / math.pi
        yaw = 0.0  # Cannot determine yaw from accelerometer alone

        return pitch, roll, yaw

    def get_specification(self) -> Dict[str, Any]:
        """Get LSM9DS1 hardware specifications.

        Returns:
            Dictionary with sensor specifications.
        """
        return {
            "name": self.name,
            "type": self.sensor_type,
            "accelerometer": {
                "range": f"±{self.ACCEL_RANGE}G",
                "resolution": f"{self.ACCEL_RESOLUTION:.6f}G/LSB",
            },
            "gyroscope": {
                "range": f"±{self.GYRO_RANGE}°/s",
                "resolution": f"{self.GYRO_RESOLUTION:.2f}°/s/LSB",
            },
            "magnetometer": {
                "range": f"±{self.MAG_RANGE}Gauss",
                "resolution": f"{self.MAG_RESOLUTION:.6f}Gauss/LSB",
            },
        }

    def validate_reading(self, value: Any) -> bool:
        """Validate IMU reading.

        Args:
            value: IMUData object to validate.

        Returns:
            bool: True if all values are within acceptable ranges.
        """
        if not isinstance(value, IMUData):
            return False

        # Check accelerometer range
        if (
            abs(value.accel_x) > self.ACCEL_RANGE
            or abs(value.accel_y) > self.ACCEL_RANGE
            or abs(value.accel_z) > self.ACCEL_RANGE
        ):
            return False

        # Check gyroscope range
        if (
            abs(value.gyro_x) > self.GYRO_RANGE
            or abs(value.gyro_y) > self.GYRO_RANGE
            or abs(value.gyro_z) > self.GYRO_RANGE
        ):
            return False

        # Check angles are reasonable (-180 to 180)
        if abs(value.pitch) > 180 or abs(value.roll) > 180 or abs(value.yaw) > 180:
            return False

        return True
