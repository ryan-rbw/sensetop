"""Unit tests for sensor modules."""

import pytest

from sensetop.sensors.base import Sensor, SensorReading, SensorStatus
from sensetop.sensors.environmental import EnvironmentalData, EnvironmentalSensor
from sensetop.sensors.imu import IMUData, IMUSensor
from sensetop.sensors.system import SystemMetrics, SystemSensor


class TestBaseSensor:
    """Tests for base Sensor class."""

    def test_sensor_properties(self):
        """Test sensor property initialization."""
        imu = IMUSensor(use_mock=True)
        assert imu.name == "IMU 9-DOF"
        assert imu.sensor_type == "LSM9DS1"
        assert imu.status == SensorStatus.OK
        assert imu.reading_count == 0
        assert imu.error_count == 0
        assert imu.error_rate == 0.0

    def test_sensor_error_tracking(self):
        """Test error tracking in sensors."""
        imu = IMUSensor(use_mock=True)
        imu.initialize()

        # Get some successful readings
        for _ in range(5):
            imu.read()

        assert imu.reading_count == 5
        assert imu.error_count == 0
        assert imu.error_rate == 0.0


class TestIMUSensor:
    """Tests for IMU sensor module."""

    def test_imu_initialization(self):
        """Test IMU sensor initialization."""
        imu = IMUSensor(use_mock=True)
        imu.initialize()
        assert imu._initialized is True

    def test_imu_read_mock(self, mock_imu_sensor):
        """Test reading from mock IMU sensor."""
        reading = mock_imu_sensor.read()

        assert isinstance(reading, SensorReading)
        assert isinstance(reading.value, IMUData)
        assert reading.status == SensorStatus.OK
        assert reading.unit == "mixed"

    def test_imu_data_structure(self, mock_imu_sensor):
        """Test IMU data structure."""
        reading = mock_imu_sensor.read()
        imu_data = reading.value

        # Check all required fields exist
        assert hasattr(imu_data, "accel_x")
        assert hasattr(imu_data, "accel_y")
        assert hasattr(imu_data, "accel_z")
        assert hasattr(imu_data, "gyro_x")
        assert hasattr(imu_data, "gyro_y")
        assert hasattr(imu_data, "gyro_z")
        assert hasattr(imu_data, "mag_x")
        assert hasattr(imu_data, "mag_y")
        assert hasattr(imu_data, "mag_z")
        assert hasattr(imu_data, "pitch")
        assert hasattr(imu_data, "roll")
        assert hasattr(imu_data, "yaw")

    def test_imu_validation(self, mock_imu_sensor):
        """Test IMU data validation."""
        reading = mock_imu_sensor.read()
        assert mock_imu_sensor.validate_reading(reading.value) is True

    def test_imu_specification(self, mock_imu_sensor):
        """Test IMU specification retrieval."""
        spec = mock_imu_sensor.get_specification()

        assert spec["name"] == "IMU 9-DOF"
        assert spec["type"] == "LSM9DS1"
        assert "accelerometer" in spec
        assert "gyroscope" in spec
        assert "magnetometer" in spec

    def test_imu_multiple_reads(self, mock_imu_sensor):
        """Test multiple successive IMU reads."""
        for _ in range(10):
            reading = mock_imu_sensor.read()
            assert reading.status == SensorStatus.OK

        assert mock_imu_sensor.reading_count == 10
        assert mock_imu_sensor.error_count == 0

    @pytest.mark.parametrize(
        "accel_x,valid",
        [
            (0.0, True),
            (8.0, True),
            (-8.0, True),
            (20.0, False),  # Out of range
            (-20.0, False),
        ],
    )
    def test_imu_accel_validation(self, mock_imu_sensor, accel_x, valid):
        """Test accelerometer range validation."""
        imu_data = IMUData(
            accel_x=accel_x,
            accel_y=0.0,
            accel_z=1.0,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
            mag_x=20.0,
            mag_y=30.0,
            mag_z=40.0,
        )
        assert mock_imu_sensor.validate_reading(imu_data) == valid

    def test_imu_read_without_initialization(self):
        """Test reading without initialization raises error."""
        sensor = IMUSensor(use_mock=True)
        # Don't initialize
        with pytest.raises(RuntimeError, match="not initialized"):
            sensor.read()

    def test_imu_orientation_calculation(self):
        """Test orientation angle calculations."""
        sensor = IMUSensor(use_mock=True)

        # Test with different accelerometer values
        pitch, roll, yaw = sensor._calculate_orientation(0.0, 0.0, 1.0)
        assert pitch == 0.0
        assert roll == 0.0
        assert yaw == 0.0

        # Test with tilted values
        pitch, roll, yaw = sensor._calculate_orientation(1.0, 0.0, 0.0)
        assert abs(roll) > 0  # Should have non-zero roll
        assert yaw == 0.0  # Yaw always 0 from accel only

    def test_imu_gyro_out_of_range(self):
        """Test gyroscope out of range validation."""
        sensor = IMUSensor(use_mock=True)
        sensor.initialize()

        imu_data = IMUData(
            accel_x=0.0,
            accel_y=0.0,
            accel_z=1.0,
            gyro_x=3000.0,  # Out of range
            gyro_y=0.0,
            gyro_z=0.0,
            mag_x=20.0,
            mag_y=30.0,
            mag_z=40.0,
        )
        assert sensor.validate_reading(imu_data) is False

    def test_imu_invalid_angles(self):
        """Test validation with invalid angles."""
        sensor = IMUSensor(use_mock=True)
        sensor.initialize()

        imu_data = IMUData(
            accel_x=0.0,
            accel_y=0.0,
            accel_z=1.0,
            gyro_x=0.0,
            gyro_y=0.0,
            gyro_z=0.0,
            mag_x=20.0,
            mag_y=30.0,
            mag_z=40.0,
            pitch=200.0,  # Invalid angle
            roll=0.0,
            yaw=0.0,
        )
        assert sensor.validate_reading(imu_data) is False

    def test_imu_validation_wrong_type(self):
        """Test validation with wrong data type."""
        sensor = IMUSensor(use_mock=True)
        sensor.initialize()

        assert sensor.validate_reading("not an IMUData") is False
        assert sensor.validate_reading(42) is False

    def test_imu_data_repr(self):
        """Test IMUData string representation."""
        imu_data = IMUData(
            accel_x=1.0,
            accel_y=2.0,
            accel_z=3.0,
            gyro_x=10.0,
            gyro_y=20.0,
            gyro_z=30.0,
            mag_x=40.0,
            mag_y=50.0,
            mag_z=60.0,
            pitch=5.0,
            roll=10.0,
            yaw=15.0,
        )
        repr_str = repr(imu_data)
        assert "IMUData" in repr_str
        assert "accel" in repr_str
        assert "gyro" in repr_str
        assert "mag" in repr_str


class TestEnvironmentalSensor:
    """Tests for environmental sensor module."""

    def test_environmental_initialization(self):
        """Test environmental sensor initialization."""
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()
        assert sensor._initialized is True

    def test_environmental_read_mock(self, mock_environmental_sensor):
        """Test reading from mock environmental sensor."""
        reading = mock_environmental_sensor.read()

        assert isinstance(reading, SensorReading)
        assert isinstance(reading.value, EnvironmentalData)
        assert reading.status == SensorStatus.OK

    def test_environmental_data_structure(self, mock_environmental_sensor):
        """Test environmental data structure."""
        reading = mock_environmental_sensor.read()
        env_data = reading.value

        assert hasattr(env_data, "temperature")
        assert hasattr(env_data, "humidity")
        assert hasattr(env_data, "pressure")
        assert hasattr(env_data, "dew_point")
        assert hasattr(env_data, "altitude")

    def test_environmental_ranges(self, mock_environmental_sensor):
        """Test environmental data is in valid ranges."""
        reading = mock_environmental_sensor.read()
        env_data = reading.value

        assert -40 <= env_data.temperature <= 120
        assert 0 <= env_data.humidity <= 100
        assert 260 <= env_data.pressure <= 1260

    def test_dew_point_calculation(self, mock_environmental_sensor):
        """Test dew point calculation."""
        # Dew point should be less than temperature
        reading = mock_environmental_sensor.read()
        env_data = reading.value

        assert env_data.dew_point <= env_data.temperature

    def test_altitude_calculation(self, mock_environmental_sensor):
        """Test altitude calculation."""
        # Sea level pressure should give ~0 altitude
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()

        # At sea level pressure
        reading = sensor.read()
        assert -1000 < reading.value.altitude < 1000

    def test_environmental_validation(self, mock_environmental_sensor):
        """Test environmental data validation."""
        reading = mock_environmental_sensor.read()
        assert mock_environmental_sensor.validate_reading(reading.value) is True

    @pytest.mark.parametrize(
        "temp,humidity,pressure,valid",
        [
            (20.0, 50.0, 1013.25, True),
            (-40.0, 0.0, 260.0, True),
            (120.0, 100.0, 1260.0, True),
            (200.0, 50.0, 1013.25, False),  # Temp too high
            (20.0, 150.0, 1013.25, False),  # Humidity too high
            (20.0, 50.0, 2000.0, False),  # Pressure too high
        ],
    )
    def test_environmental_validation_ranges(self, temp, humidity, pressure, valid):
        """Test environmental sensor validation."""
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()

        env_data = EnvironmentalData(
            temperature=temp,
            humidity=humidity,
            pressure=pressure,
            dew_point=temp - 5,
            altitude=0.0,
        )
        assert sensor.validate_reading(env_data) == valid

    def test_environmental_read_without_initialization(self):
        """Test reading without initialization raises error."""
        sensor = EnvironmentalSensor(use_mock=True)
        with pytest.raises(RuntimeError, match="not initialized"):
            sensor.read()

    def test_dew_point_zero_humidity(self):
        """Test dew point calculation with zero humidity."""
        sensor = EnvironmentalSensor(use_mock=True)

        # With zero humidity, dew point should equal temperature
        dew_point = sensor._calculate_dew_point(20.0, 0.0)
        assert dew_point == 20.0

    def test_dew_point_high_humidity(self):
        """Test dew point calculation with high humidity."""
        sensor = EnvironmentalSensor(use_mock=True)

        # With 100% humidity, dew point should be close to temperature
        dew_point = sensor._calculate_dew_point(20.0, 100.0)
        assert abs(dew_point - 20.0) < 1.0

    def test_altitude_various_pressures(self):
        """Test altitude calculation at various pressures."""
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()

        # High pressure (below sea level) should give negative altitude
        altitude_high = sensor._calculate_altitude(1050.0)
        assert altitude_high < 0

        # Low pressure (high altitude) should give positive altitude
        altitude_low = sensor._calculate_altitude(900.0)
        assert altitude_low > 0

    def test_altitude_zero_pressure(self):
        """Test altitude calculation with zero pressure."""
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()

        altitude = sensor._calculate_altitude(0.0)
        assert altitude == 0.0

    def test_environmental_validation_wrong_type(self):
        """Test validation with wrong data type."""
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()

        assert sensor.validate_reading("not environmental data") is False
        assert sensor.validate_reading(123) is False

    def test_environmental_dew_point_validation(self):
        """Test validation fails when dew point exceeds temperature."""
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()

        env_data = EnvironmentalData(
            temperature=20.0,
            humidity=50.0,
            pressure=1013.25,
            dew_point=25.0,  # Dew point higher than temperature (invalid)
            altitude=0.0,
        )
        assert sensor.validate_reading(env_data) is False

    def test_environmental_data_repr(self):
        """Test EnvironmentalData string representation."""
        env_data = EnvironmentalData(
            temperature=22.5,
            humidity=45.0,
            pressure=1013.25,
            dew_point=11.5,
            altitude=100.0,
        )
        repr_str = repr(env_data)
        assert "EnvironmentalData" in repr_str
        assert "22.5" in repr_str
        assert "45.0" in repr_str


class TestSystemSensor:
    """Tests for system metrics sensor module."""

    def test_system_initialization(self):
        """Test system sensor initialization."""
        sensor = SystemSensor(use_mock=True)
        sensor.initialize()
        assert sensor._initialized is True

    def test_system_read_mock(self, mock_system_sensor):
        """Test reading from mock system sensor."""
        reading = mock_system_sensor.read()

        assert isinstance(reading, SensorReading)
        assert isinstance(reading.value, SystemMetrics)
        assert reading.status == SensorStatus.OK

    def test_system_data_structure(self, mock_system_sensor):
        """Test system metrics data structure."""
        reading = mock_system_sensor.read()
        metrics = reading.value

        assert hasattr(metrics, "cpu_temp")
        assert hasattr(metrics, "memory_total")
        assert hasattr(metrics, "memory_used")
        assert hasattr(metrics, "memory_available")
        assert hasattr(metrics, "uptime")
        assert hasattr(metrics, "cpu_count")

    def test_memory_percentage(self, mock_system_sensor):
        """Test memory percentage calculation."""
        reading = mock_system_sensor.read()
        metrics = reading.value

        memory_percent = metrics.memory_percent
        assert 0 <= memory_percent <= 100

    def test_system_validation(self, mock_system_sensor):
        """Test system metrics validation."""
        reading = mock_system_sensor.read()
        assert mock_system_sensor.validate_reading(reading.value) is True

    def test_system_specification(self, mock_system_sensor):
        """Test system specification retrieval."""
        spec = mock_system_sensor.get_specification()

        assert spec["name"] == "System Metrics"
        assert spec["type"] == "RaspberryPi System"
        assert "cpu_count" in spec
        assert "temperature" in spec
        assert "data_sources" in spec

    @pytest.mark.parametrize(
        "cpu_temp,memory_used,valid",
        [
            (45.0, 1000000, True),
            (0.0, 0, True),
            (100.0, 4000000000, True),
            (200.0, 1000000, False),  # Temp too high
            (45.0, -1000000, False),  # Negative memory
        ],
    )
    def test_system_validation_ranges(self, cpu_temp, memory_used, valid):
        """Test system sensor validation."""
        from datetime import timedelta

        sensor = SystemSensor(use_mock=True)
        sensor.initialize()

        metrics = SystemMetrics(
            cpu_temp=cpu_temp,
            memory_total=4000000000,
            memory_used=memory_used,
            memory_available=3000000000,
            uptime=timedelta(hours=1),
            cpu_count=4,
        )
        assert sensor.validate_reading(metrics) == valid

    def test_system_read_without_initialization(self):
        """Test reading without initialization raises error."""
        sensor = SystemSensor(use_mock=True)
        with pytest.raises(RuntimeError, match="not initialized"):
            sensor.read()

    def test_memory_percent_zero_total(self):
        """Test memory percentage with zero total memory."""
        from datetime import timedelta

        metrics = SystemMetrics(
            cpu_temp=45.0,
            memory_total=0,  # Zero total
            memory_used=0,
            memory_available=0,
            uptime=timedelta(hours=1),
            cpu_count=4,
        )
        assert metrics.memory_percent == 0.0

    def test_memory_percent_calculation(self):
        """Test memory percentage calculation."""
        from datetime import timedelta

        metrics = SystemMetrics(
            cpu_temp=45.0,
            memory_total=1000,
            memory_used=250,
            memory_available=750,
            uptime=timedelta(hours=1),
            cpu_count=4,
        )
        assert metrics.memory_percent == 25.0

    def test_system_validation_memory_exceeds_total(self):
        """Test validation fails when memory used exceeds total."""
        from datetime import timedelta

        sensor = SystemSensor(use_mock=True)
        sensor.initialize()

        metrics = SystemMetrics(
            cpu_temp=45.0,
            memory_total=1000,
            memory_used=1500,  # Exceeds total
            memory_available=0,
            uptime=timedelta(hours=1),
            cpu_count=4,
        )
        assert sensor.validate_reading(metrics) is False

    def test_system_validation_negative_uptime(self):
        """Test validation fails with negative uptime."""
        from datetime import timedelta

        sensor = SystemSensor(use_mock=True)
        sensor.initialize()

        metrics = SystemMetrics(
            cpu_temp=45.0,
            memory_total=1000,
            memory_used=500,
            memory_available=500,
            uptime=timedelta(hours=-1),  # Negative
            cpu_count=4,
        )
        assert sensor.validate_reading(metrics) is False

    def test_system_validation_wrong_type(self):
        """Test validation with wrong data type."""
        sensor = SystemSensor(use_mock=True)
        sensor.initialize()

        assert sensor.validate_reading("not system metrics") is False
        assert sensor.validate_reading(42) is False

    def test_system_metrics_repr(self):
        """Test SystemMetrics string representation."""
        from datetime import timedelta

        metrics = SystemMetrics(
            cpu_temp=45.5,
            memory_total=4294967296,
            memory_used=1610612736,
            memory_available=2684354560,
            uptime=timedelta(hours=10, minutes=30),
            cpu_count=4,
        )
        repr_str = repr(metrics)
        assert "SystemMetrics" in repr_str
        assert "45.5" in repr_str
        assert "cpu_temp" in repr_str


class TestSensorShutdown:
    """Tests for sensor shutdown and cleanup."""

    def test_imu_shutdown(self):
        """Test IMU sensor shutdown."""
        sensor = IMUSensor(use_mock=True)
        sensor.initialize()
        sensor.shutdown()
        assert sensor._initialized is False

    def test_environmental_shutdown(self):
        """Test environmental sensor shutdown."""
        sensor = EnvironmentalSensor(use_mock=True)
        sensor.initialize()
        sensor.shutdown()
        assert sensor._initialized is False

    def test_system_shutdown(self):
        """Test system sensor shutdown."""
        sensor = SystemSensor(use_mock=True)
        sensor.initialize()
        sensor.shutdown()
        assert sensor._initialized is False
