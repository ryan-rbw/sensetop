"""Unit tests for threshold and alarm management."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from sensetop.data.alarms import AlarmEvent, AlarmManager, AlarmSeverity
from sensetop.data.thresholds import SensorThreshold, ThresholdManager


class TestSensorThreshold:
    """Tests for sensor threshold configuration."""

    def test_threshold_creation(self):
        """Test creating a threshold."""
        threshold = SensorThreshold(
            sensor_name="temperature",
            min_value=0.0,
            max_value=50.0,
        )
        assert threshold.sensor_name == "temperature"
        assert threshold.min_value == 0.0
        assert threshold.max_value == 50.0

    def test_threshold_validation(self):
        """Test threshold validation."""
        # Valid threshold
        threshold = SensorThreshold("temp", min_value=0.0, max_value=100.0)
        threshold.validate()  # Should not raise

        # Invalid: min > max
        threshold_bad = SensorThreshold("temp", min_value=100.0, max_value=0.0)
        with pytest.raises(ValueError):
            threshold_bad.validate()

    def test_threshold_check_ok(self):
        """Test value check in OK range."""
        threshold = SensorThreshold("temperature", min_value=0.0, max_value=50.0)
        status, violated = threshold.check_value(25.0)
        assert status == "ok"
        assert not violated

    def test_threshold_check_warning(self):
        """Test value check in warning range."""
        threshold = SensorThreshold("temperature", min_value=0.0, max_value=50.0)
        status, violated = threshold.check_value(-10.0)
        assert status == "warning"
        assert violated

    def test_threshold_check_critical(self):
        """Test value check in critical range."""
        threshold = SensorThreshold(
            "temperature",
            min_value=0.0,
            max_value=50.0,
            critical_min=-40.0,
            critical_max=80.0,
        )
        status, violated = threshold.check_value(85.0)
        assert status == "critical"
        assert violated

    def test_threshold_disabled(self):
        """Test that disabled threshold always returns OK."""
        threshold = SensorThreshold("temperature", min_value=0.0, max_value=50.0, enabled=False)
        status, violated = threshold.check_value(100.0)
        assert status == "ok"
        assert not violated


class TestThresholdManager:
    """Tests for threshold management."""

    def test_manager_creation(self):
        """Test manager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            assert len(manager.get_all_thresholds()) > 0

    def test_manager_defaults(self):
        """Test default thresholds are loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            thresholds = manager.get_all_thresholds()

            assert "temperature" in thresholds
            assert "humidity" in thresholds
            assert "pressure" in thresholds

    def test_set_threshold(self):
        """Test setting a threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))

            new_threshold = SensorThreshold("custom_sensor", min_value=10.0, max_value=90.0)
            manager.set_threshold(new_threshold)

            retrieved = manager.get_threshold("custom_sensor")
            assert retrieved is not None
            assert retrieved.min_value == 10.0

    def test_check_value(self):
        """Test checking values through manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))

            # Temperature should be OK at 20°C
            status, violated = manager.check_value("temperature", 20.0)
            assert status == "ok"
            assert not violated

            # Temperature should be critical at 85°C
            status, violated = manager.check_value("temperature", 85.0)
            assert status == "critical"
            assert violated

    def test_save_and_load(self):
        """Test saving and loading thresholds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = str(Path(tmpdir) / "thresholds.json")

            # Create manager and modify a threshold
            manager1 = ThresholdManager(config_file=config_file)
            threshold = manager1.get_threshold("temperature")
            # Modify with valid constraint: critical_min <= min_value, critical_max >= max_value
            threshold.min_value = -20.0
            threshold.max_value = 60.0
            threshold.critical_min = -50.0
            threshold.critical_max = 90.0
            manager1.set_threshold(threshold)
            manager1.save_to_file()

            # Load in new manager
            manager2 = ThresholdManager(config_file=config_file)
            loaded = manager2.get_threshold("temperature")
            assert loaded.min_value == -20.0
            assert loaded.max_value == 60.0
            assert loaded.critical_min == -50.0
            assert loaded.critical_max == 90.0

    def test_reset_to_defaults(self):
        """Test resetting to defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))

            # Modify a threshold (keeping critical values valid: critical_min <= min_value, critical_max >= max_value)
            threshold = manager.get_threshold("temperature")
            original_min = threshold.min_value
            original_max = threshold.max_value
            threshold.min_value = 5.0
            threshold.max_value = 70.0
            threshold.critical_min = -50.0  # Must be <= min_value
            manager.set_threshold(threshold)

            # Verify it was modified
            assert manager.get_threshold("temperature").min_value == 5.0

            # Reset and verify
            manager.reset_to_defaults()
            threshold = manager.get_threshold("temperature")
            assert threshold.min_value == original_min
            assert threshold.max_value == original_max

    def test_enable_disable_sensor(self):
        """Test enabling/disabling sensor thresholds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))

            manager.disable_sensor("temperature")
            threshold = manager.get_threshold("temperature")
            assert not threshold.enabled

            manager.enable_sensor("temperature")
            threshold = manager.get_threshold("temperature")
            assert threshold.enabled


class TestAlarmEvent:
    """Tests for alarm events."""

    def test_alarm_event_creation(self):
        """Test creating an alarm event."""
        alarm = AlarmEvent(
            sensor_name="temperature",
            value=85.0,
            severity=AlarmSeverity.CRITICAL,
            timestamp=datetime.now(),
            message="Temperature too high",
        )
        assert alarm.sensor_name == "temperature"
        assert alarm.value == 85.0
        assert alarm.severity == AlarmSeverity.CRITICAL
        assert not alarm.acknowledged

    def test_alarm_event_acknowledge(self):
        """Test acknowledging an alarm."""
        alarm = AlarmEvent(
            sensor_name="temperature",
            value=85.0,
            severity=AlarmSeverity.CRITICAL,
            timestamp=datetime.now(),
            message="Temperature too high",
        )
        assert not alarm.acknowledged
        alarm.acknowledged = True
        assert alarm.acknowledged


class TestAlarmManager:
    """Tests for alarm management."""

    def test_alarm_manager_creation(self):
        """Test creating alarm manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)
            assert len(alarm_manager.get_active_alarms()) == 0

    def test_check_value_no_alarm(self):
        """Test checking value that doesn't violate threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            alarm = alarm_manager.check_and_create_alarm("temperature", 25.0)
            assert alarm is None
            assert len(alarm_manager.get_active_alarms()) == 0

    def test_check_value_creates_alarm(self):
        """Test checking value that violates threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            alarm = alarm_manager.check_and_create_alarm("temperature", 85.0)
            assert alarm is not None
            assert alarm.severity == AlarmSeverity.CRITICAL
            assert len(alarm_manager.get_active_alarms()) == 1

    def test_acknowledge_alarm(self):
        """Test acknowledging an alarm."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            alarm_manager.check_and_create_alarm("temperature", 85.0)
            result = alarm_manager.acknowledge_alarm("temperature")
            assert result is True

            active = alarm_manager.get_active_alarms()
            assert active[0].acknowledged

    def test_get_critical_alarms(self):
        """Test getting critical alarms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            # Create a warning alarm (humidity: min=30, max=70; use 20 for warning)
            alarm_manager.check_and_create_alarm("humidity", 20.0)
            # Create a critical alarm (temperature: critical_max=80; use 85 for critical)
            alarm_manager.check_and_create_alarm("temperature", 85.0)

            critical = alarm_manager.get_active_critical_alarms()
            assert len(critical) == 1
            assert critical[0].sensor_name == "temperature"

    def test_alarm_history(self):
        """Test alarm history tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            alarm_manager.check_and_create_alarm("temperature", 85.0)
            alarm_manager.check_and_create_alarm("humidity", 5.0)

            history = alarm_manager.get_alarm_history()
            assert len(history) == 2

    def test_alarm_history_limit(self):
        """Test getting limited alarm history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            alarm_manager.check_and_create_alarm("temperature", 85.0)
            alarm_manager.check_and_create_alarm("humidity", 5.0)
            alarm_manager.check_and_create_alarm("pressure", 2000.0)

            history = alarm_manager.get_alarm_history(limit=2)
            assert len(history) == 2

    def test_has_active_alarms(self):
        """Test checking if there are active alarms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            assert not alarm_manager.has_active_alarms()

            alarm_manager.check_and_create_alarm("temperature", 85.0)
            assert alarm_manager.has_active_alarms()

    def test_has_critical_alarms(self):
        """Test checking if there are critical alarms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            assert not alarm_manager.has_critical_alarms()

            alarm_manager.check_and_create_alarm("temperature", 85.0)
            assert alarm_manager.has_critical_alarms()

    def test_acknowledge_all(self):
        """Test acknowledging all alarms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            threshold_manager = ThresholdManager(config_file=str(Path(tmpdir) / "thresholds.json"))
            alarm_manager = AlarmManager(threshold_manager)

            alarm_manager.check_and_create_alarm("temperature", 85.0)
            alarm_manager.check_and_create_alarm("humidity", 5.0)

            count = alarm_manager.acknowledge_all()
            assert count == 2

            unacked = alarm_manager.get_unacknowledged_alarms()
            assert len(unacked) == 0
