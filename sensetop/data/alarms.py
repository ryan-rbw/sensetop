"""Alarm and event tracking system."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sensetop.data.thresholds import ThresholdManager


class AlarmSeverity(Enum):
    """Alarm severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlarmEvent:
    """A single alarm event."""

    sensor_name: str
    value: float
    severity: AlarmSeverity
    timestamp: datetime
    message: str
    acknowledged: bool = False

    def __repr__(self) -> str:
        """String representation."""
        ack_str = " [ACK]" if self.acknowledged else ""
        return (
            f"AlarmEvent({self.sensor_name}, value={self.value}, "
            f"severity={self.severity.value}, time={self.timestamp.isoformat()}"
            f"{ack_str})"
        )


class AlarmManager:
    """Manage alarm events and history."""

    def __init__(
        self,
        threshold_manager: ThresholdManager,
        max_history: int = 500,
    ) -> None:
        """Initialize alarm manager.

        Args:
            threshold_manager: ThresholdManager instance.
            max_history: Maximum number of alarm events to keep.
        """
        self.threshold_manager = threshold_manager
        self.max_history = max_history
        self._alarm_history: List[AlarmEvent] = []
        self._active_alarms: dict = {}  # sensor_name -> AlarmEvent

    def check_and_create_alarm(
        self,
        sensor_name: str,
        value: float,
    ) -> Optional[AlarmEvent]:
        """Check sensor value and create alarm if threshold violated.

        Args:
            sensor_name: Name of the sensor.
            value: The sensor value.

        Returns:
            AlarmEvent if threshold violated, None otherwise.
        """
        status, violated = self.threshold_manager.check_value(sensor_name, value)

        if not violated:
            # Clear active alarm for this sensor if it was violated before
            if sensor_name in self._active_alarms:
                del self._active_alarms[sensor_name]
            return None

        # Create alarm event
        severity = AlarmSeverity.CRITICAL if status == "critical" else AlarmSeverity.WARNING
        message = f"{sensor_name} value {value:.2f} exceeds threshold ({status})"

        alarm = AlarmEvent(
            sensor_name=sensor_name,
            value=value,
            severity=severity,
            timestamp=datetime.now(),
            message=message,
        )

        # Track active alarm
        self._active_alarms[sensor_name] = alarm

        # Add to history
        self._alarm_history.append(alarm)

        # Trim history if needed
        if len(self._alarm_history) > self.max_history:
            self._alarm_history = self._alarm_history[-self.max_history :]

        return alarm

    def acknowledge_alarm(self, sensor_name: str) -> bool:
        """Acknowledge an active alarm.

        Args:
            sensor_name: Name of the sensor with active alarm.

        Returns:
            True if alarm was acknowledged, False if no active alarm.
        """
        if sensor_name in self._active_alarms:
            self._active_alarms[sensor_name].acknowledged = True
            return True
        return False

    def acknowledge_all(self) -> int:
        """Acknowledge all active alarms.

        Returns:
            Number of alarms acknowledged.
        """
        count = 0
        for alarm in self._active_alarms.values():
            if not alarm.acknowledged:
                alarm.acknowledged = True
                count += 1
        return count

    def get_active_alarms(self) -> List[AlarmEvent]:
        """Get all active alarms.

        Returns:
            List of active alarm events.
        """
        return list(self._active_alarms.values())

    def get_active_critical_alarms(self) -> List[AlarmEvent]:
        """Get active critical alarms.

        Returns:
            List of critical alarm events.
        """
        return [
            alarm
            for alarm in self._active_alarms.values()
            if alarm.severity == AlarmSeverity.CRITICAL
        ]

    def get_unacknowledged_alarms(self) -> List[AlarmEvent]:
        """Get unacknowledged active alarms.

        Returns:
            List of unacknowledged alarm events.
        """
        return [alarm for alarm in self._active_alarms.values() if not alarm.acknowledged]

    def get_alarm_history(self, limit: Optional[int] = None) -> List[AlarmEvent]:
        """Get alarm history.

        Args:
            limit: Maximum number of recent alarms to return.

        Returns:
            List of alarm events (most recent last).
        """
        if limit is None:
            return self._alarm_history.copy()
        return self._alarm_history[-limit:]

    def get_sensor_alarm_count(self, sensor_name: str) -> int:
        """Get total alarm count for a sensor.

        Args:
            sensor_name: Name of the sensor.

        Returns:
            Number of alarms in history for this sensor.
        """
        return sum(1 for alarm in self._alarm_history if alarm.sensor_name == sensor_name)

    def clear_history(self) -> None:
        """Clear all alarm history."""
        self._alarm_history.clear()

    def has_active_alarms(self) -> bool:
        """Check if there are any active alarms."""
        return len(self._active_alarms) > 0

    def has_critical_alarms(self) -> bool:
        """Check if there are any critical alarms."""
        return any(
            alarm.severity == AlarmSeverity.CRITICAL for alarm in self._active_alarms.values()
        )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AlarmManager(active={len(self._active_alarms)}, "
            f"history={len(self._alarm_history)})"
        )
