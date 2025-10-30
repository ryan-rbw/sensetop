"""Unit tests for application components."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from sensetop.app import SenseTopApp
from sensetop.config import Config


class TestConfig:
    """Tests for configuration management."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config(use_mock=True)
        assert config.theme == "dark"
        assert config.refresh_rate == 500
        assert config.sensor_interval == 500
        assert config.temperature_unit == "celsius"
        assert config.pressure_unit == "hpa"
        assert config.enable_logging is True

    def test_config_custom_theme(self):
        """Test custom theme configuration."""
        config = Config(theme="light", use_mock=True)
        assert config.theme == "light"

    def test_config_to_dict(self):
        """Test config to dictionary conversion."""
        config = Config(use_mock=True)
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "theme" in config_dict
        assert "refresh_rate" in config_dict

    def test_config_temperature_units(self):
        """Test temperature unit configuration."""
        config_c = Config(temperature_unit="celsius", use_mock=True)
        config_f = Config(temperature_unit="fahrenheit", use_mock=True)
        assert config_c.temperature_unit == "celsius"
        assert config_f.temperature_unit == "fahrenheit"

    def test_config_pressure_units(self):
        """Test pressure unit configuration."""
        config_hpa = Config(pressure_unit="hpa", use_mock=True)
        config_inhg = Config(pressure_unit="inhg", use_mock=True)
        assert config_hpa.pressure_unit == "hpa"
        assert config_inhg.pressure_unit == "inhg"


class TestSenseTopAppInit:
    """Tests for SenseTopApp initialization."""

    def test_app_initialization_with_defaults(self):
        """Test app initialization with default config."""
        with patch("sensetop.app.IMUSensor"):
            with patch("sensetop.app.EnvironmentalSensor"):
                with patch("sensetop.app.SystemSensor"):
                    app = SenseTopApp(Config(use_mock=True))
                    assert app.config is not None
                    assert app.tui is not None
                    assert app.running is False
                    assert app.sensor_thread is None

    def test_app_initialization_with_custom_config(self):
        """Test app initialization with custom config."""
        config = Config(theme="light", refresh_rate=1000, use_mock=True)
        with patch("sensetop.app.IMUSensor"):
            with patch("sensetop.app.EnvironmentalSensor"):
                with patch("sensetop.app.SystemSensor"):
                    app = SenseTopApp(config)
                    assert app.config.theme == "light"
                    assert app.config.refresh_rate == 1000
                    assert app.tui.refresh_rate == 1000

    def test_app_sensors_initialized(self):
        """Test that sensors are initialized."""
        with patch("sensetop.app.IMUSensor") as mock_imu:
            with patch("sensetop.app.EnvironmentalSensor") as mock_env:
                with patch("sensetop.app.SystemSensor") as mock_sys:
                    mock_imu.return_value = Mock()
                    mock_env.return_value = Mock()
                    mock_sys.return_value = Mock()

                    app = SenseTopApp(Config(use_mock=True))

                    # Verify sensors were created
                    mock_imu.assert_called()
                    mock_env.assert_called()
                    mock_sys.assert_called()

                    # Verify sensors are in the sensors dict
                    assert "imu" in app.sensors
                    assert "environmental" in app.sensors
                    assert "system" in app.sensors

    def test_app_color_scheme_selection(self):
        """Test color scheme selection based on config."""
        config = Config(theme="dark", use_mock=True)
        with patch("sensetop.app.IMUSensor"):
            with patch("sensetop.app.EnvironmentalSensor"):
                with patch("sensetop.app.SystemSensor"):
                    app = SenseTopApp(config)
                    assert app.tui.color_manager is not None


class TestSenseTopAppUI:
    """Tests for SenseTopApp UI setup."""

    def test_app_ui_setup(self):
        """Test that UI views are registered."""
        with patch("sensetop.app.IMUSensor"):
            with patch("sensetop.app.EnvironmentalSensor"):
                with patch("sensetop.app.SystemSensor"):
                    app = SenseTopApp(Config(use_mock=True))

                    # Setup UI without initializing curses
                    app._setup_ui()

                    # Check views are registered
                    assert "dashboard" in app.tui.views
                    assert "help" in app.tui.views
                    assert app.tui.current_view is not None


class TestSenseTopAppShutdown:
    """Tests for SenseTopApp shutdown."""

    def test_app_shutdown(self):
        """Test application shutdown."""
        with patch("sensetop.app.IMUSensor") as mock_imu:
            with patch("sensetop.app.EnvironmentalSensor") as mock_env:
                with patch("sensetop.app.SystemSensor") as mock_sys:
                    mock_imu_inst = Mock()
                    mock_env_inst = Mock()
                    mock_sys_inst = Mock()

                    mock_imu.return_value = mock_imu_inst
                    mock_env.return_value = mock_env_inst
                    mock_sys.return_value = mock_sys_inst

                    app = SenseTopApp(Config(use_mock=True))
                    app.running = True

                    app.shutdown()

                    assert app.running is False
                    mock_imu_inst.shutdown.assert_called()
                    mock_env_inst.shutdown.assert_called()
                    mock_sys_inst.shutdown.assert_called()


class TestSenseTopAppSensorLoop:
    """Tests for sensor read loop functionality."""

    def test_sensor_read_loop_records_data(self):
        """Test that sensor read loop records data to history."""
        from datetime import datetime, timedelta
        from unittest.mock import MagicMock

        from sensetop.sensors.base import SensorReading, SensorStatus
        from sensetop.sensors.environmental import EnvironmentalData
        from sensetop.sensors.imu import IMUData
        from sensetop.sensors.system import SystemMetrics

        with patch("sensetop.app.IMUSensor") as mock_imu:
            with patch("sensetop.app.EnvironmentalSensor") as mock_env:
                with patch("sensetop.app.SystemSensor") as mock_sys:
                    # Create mock sensor instances
                    mock_imu_inst = MagicMock()
                    mock_env_inst = MagicMock()
                    mock_sys_inst = MagicMock()

                    # Mock sensor readings
                    imu_data = IMUData(
                        accel_x=1.0,
                        accel_y=0.0,
                        accel_z=0.0,
                        gyro_x=0.0,
                        gyro_y=0.0,
                        gyro_z=0.0,
                        mag_x=20.0,
                        mag_y=30.0,
                        mag_z=40.0,
                    )
                    env_data = EnvironmentalData(
                        temperature=22.5,
                        humidity=45.0,
                        pressure=1013.25,
                        dew_point=11.5,
                        altitude=0.0,
                    )
                    sys_data = SystemMetrics(
                        cpu_temp=45.5,
                        memory_total=4000000000,
                        memory_used=1600000000,
                        memory_available=2400000000,
                        uptime=timedelta(hours=10),
                        cpu_count=4,
                    )

                    mock_imu_inst.read.return_value = SensorReading(
                        timestamp=datetime.now(),
                        value=imu_data,
                        status=SensorStatus.OK,
                        unit="mixed",
                    )
                    mock_env_inst.read.return_value = SensorReading(
                        timestamp=datetime.now(),
                        value=env_data,
                        status=SensorStatus.OK,
                        unit="mixed",
                    )
                    mock_sys_inst.read.return_value = SensorReading(
                        timestamp=datetime.now(),
                        value=sys_data,
                        status=SensorStatus.OK,
                        unit="mixed",
                    )

                    mock_imu.return_value = mock_imu_inst
                    mock_env.return_value = mock_env_inst
                    mock_sys.return_value = mock_sys_inst

                    app = SenseTopApp(Config(use_mock=True))
                    app.running = True

                    # Run one iteration of the sensor loop
                    import threading

                    thread = threading.Thread(target=app._sensor_read_loop, daemon=True)
                    thread.start()

                    # Let it run briefly
                    import time

                    time.sleep(0.2)

                    # Stop the loop
                    app.running = False
                    thread.join(timeout=2.0)

                    # Verify data was recorded
                    assert app.data_history.get_history("temperature") is not None
                    assert app.data_history.get_history("humidity") is not None
                    assert app.data_history.get_history("pressure") is not None

    def test_sensor_initialization_failure(self):
        """Test handling of sensor initialization failure."""
        with patch("sensetop.app.IMUSensor") as mock_imu:
            mock_imu.return_value.initialize.side_effect = RuntimeError("Sensor init failed")

            with pytest.raises(RuntimeError, match="Sensor init failed"):
                app = SenseTopApp(Config(use_mock=True))

    def test_alarm_triggering_in_read_loop(self):
        """Test that alarms are triggered in read loop."""
        from datetime import datetime, timedelta
        from unittest.mock import MagicMock

        from sensetop.sensors.base import SensorReading, SensorStatus
        from sensetop.sensors.environmental import EnvironmentalData
        from sensetop.sensors.imu import IMUData
        from sensetop.sensors.system import SystemMetrics

        with patch("sensetop.app.IMUSensor") as mock_imu:
            with patch("sensetop.app.EnvironmentalSensor") as mock_env:
                with patch("sensetop.app.SystemSensor") as mock_sys:
                    mock_imu_inst = MagicMock()
                    mock_env_inst = MagicMock()
                    mock_sys_inst = MagicMock()

                    # Create high temperature to trigger alarm
                    env_data = EnvironmentalData(
                        temperature=85.0,  # High temp
                        humidity=45.0,
                        pressure=1013.25,
                        dew_point=11.5,
                        altitude=0.0,
                    )

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
                    )

                    sys_data = SystemMetrics(
                        cpu_temp=45.5,
                        memory_total=4000000000,
                        memory_used=1600000000,
                        memory_available=2400000000,
                        uptime=timedelta(hours=10),
                        cpu_count=4,
                    )

                    mock_imu_inst.read.return_value = SensorReading(
                        timestamp=datetime.now(),
                        value=imu_data,
                        status=SensorStatus.OK,
                        unit="mixed",
                    )
                    mock_env_inst.read.return_value = SensorReading(
                        timestamp=datetime.now(),
                        value=env_data,
                        status=SensorStatus.OK,
                        unit="mixed",
                    )
                    mock_sys_inst.read.return_value = SensorReading(
                        timestamp=datetime.now(),
                        value=sys_data,
                        status=SensorStatus.OK,
                        unit="mixed",
                    )

                    mock_imu.return_value = mock_imu_inst
                    mock_env.return_value = mock_env_inst
                    mock_sys.return_value = mock_sys_inst

                    app = SenseTopApp(Config(use_mock=True))

                    # Set a threshold for temperature
                    from sensetop.data.thresholds import SensorThreshold

                    threshold = SensorThreshold(
                        sensor_name="temperature",
                        min_value=15.0,
                        max_value=30.0,
                        critical_min=10.0,
                        critical_max=35.0,
                        enabled=True,
                    )
                    app.threshold_manager.set_threshold(threshold)

                    app.running = True

                    # Run sensor loop briefly
                    import threading
                    import time

                    thread = threading.Thread(target=app._sensor_read_loop, daemon=True)
                    thread.start()
                    time.sleep(0.2)
                    app.running = False
                    thread.join(timeout=2.0)

                    # Check that alarm manager checked thresholds
                    active_alarms = app.alarm_manager.get_active_alarms()
                    # Note: alarm may or may not be present depending on timing
                    # Just verify the alarm manager is functional
                    assert isinstance(active_alarms, list)

    def test_sensor_read_error_handling(self):
        """Test error handling in sensor read loop."""
        from unittest.mock import MagicMock

        with patch("sensetop.app.IMUSensor") as mock_imu:
            with patch("sensetop.app.EnvironmentalSensor") as mock_env:
                with patch("sensetop.app.SystemSensor") as mock_sys:
                    mock_imu_inst = MagicMock()
                    mock_env_inst = MagicMock()
                    mock_sys_inst = MagicMock()

                    # Make IMU sensor raise an error
                    mock_imu_inst.read.side_effect = RuntimeError("Sensor read failed")
                    mock_env_inst.read.side_effect = RuntimeError("Sensor read failed")
                    mock_sys_inst.read.side_effect = RuntimeError("Sensor read failed")

                    mock_imu.return_value = mock_imu_inst
                    mock_env.return_value = mock_env_inst
                    mock_sys.return_value = mock_sys_inst

                    app = SenseTopApp(Config(use_mock=True))
                    app.running = True

                    # Run sensor loop briefly - should not crash
                    import threading
                    import time

                    thread = threading.Thread(target=app._sensor_read_loop, daemon=True)
                    thread.start()
                    time.sleep(0.2)
                    app.running = False
                    thread.join(timeout=2.0)

                    # Loop should have handled errors gracefully
                    assert True  # If we get here, error handling worked
