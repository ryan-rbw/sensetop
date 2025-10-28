"""Unit tests for application components."""

import pytest
from unittest.mock import Mock, patch, MagicMock

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
        with patch('sensetop.app.IMUSensor'):
            with patch('sensetop.app.EnvironmentalSensor'):
                with patch('sensetop.app.SystemSensor'):
                    app = SenseTopApp(Config(use_mock=True))
                    assert app.config is not None
                    assert app.tui is not None
                    assert app.running is False
                    assert app.sensor_thread is None

    def test_app_initialization_with_custom_config(self):
        """Test app initialization with custom config."""
        config = Config(theme="light", refresh_rate=1000, use_mock=True)
        with patch('sensetop.app.IMUSensor'):
            with patch('sensetop.app.EnvironmentalSensor'):
                with patch('sensetop.app.SystemSensor'):
                    app = SenseTopApp(config)
                    assert app.config.theme == "light"
                    assert app.config.refresh_rate == 1000
                    assert app.tui.refresh_rate == 1000

    def test_app_sensors_initialized(self):
        """Test that sensors are initialized."""
        with patch('sensetop.app.IMUSensor') as mock_imu:
            with patch('sensetop.app.EnvironmentalSensor') as mock_env:
                with patch('sensetop.app.SystemSensor') as mock_sys:
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
        with patch('sensetop.app.IMUSensor'):
            with patch('sensetop.app.EnvironmentalSensor'):
                with patch('sensetop.app.SystemSensor'):
                    app = SenseTopApp(config)
                    assert app.tui.color_manager is not None


class TestSenseTopAppUI:
    """Tests for SenseTopApp UI setup."""

    def test_app_ui_setup(self):
        """Test that UI views are registered."""
        with patch('sensetop.app.IMUSensor'):
            with patch('sensetop.app.EnvironmentalSensor'):
                with patch('sensetop.app.SystemSensor'):
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
        with patch('sensetop.app.IMUSensor') as mock_imu:
            with patch('sensetop.app.EnvironmentalSensor') as mock_env:
                with patch('sensetop.app.SystemSensor') as mock_sys:
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
