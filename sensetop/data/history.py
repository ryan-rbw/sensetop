"""Historical data management and statistics tracking."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

from sensetop.data.buffer import BufferEntry, CircularBuffer


@dataclass
class DataStatistics:
    """Statistical summary of historical data."""

    min_value: float
    max_value: float
    avg_value: float
    latest_value: float
    sample_count: int
    time_span: timedelta = field(default_factory=lambda: timedelta(0))

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"DataStatistics(min={self.min_value:.2f}, max={self.max_value:.2f}, "
            f"avg={self.avg_value:.2f}, latest={self.latest_value:.2f}, "
            f"samples={self.sample_count})"
        )


class SensorHistory:
    """Manage historical data for a single sensor.

    Tracks all readings with timestamps and provides statistical analysis.
    """

    def __init__(
        self, sensor_name: str, buffer_capacity: int = 120
    ) -> None:
        """Initialize sensor history.

        Args:
            sensor_name: Name of the sensor (e.g., 'temperature', 'humidity').
            buffer_capacity: Size of circular buffer for storing readings.
        """
        self.sensor_name = sensor_name
        self.buffer: CircularBuffer[float] = CircularBuffer(buffer_capacity)

    def add_reading(self, value: float, timestamp: Optional[datetime] = None) -> None:
        """Add a sensor reading to history.

        Args:
            value: The sensor reading value.
            timestamp: Timestamp for the reading. If None, uses current time.
        """
        self.buffer.append(value, timestamp)

    def get_statistics(self) -> Optional[DataStatistics]:
        """Calculate statistics for all historical data.

        Returns:
            DataStatistics object or None if no data.
        """
        entries = self.buffer.get_all()
        if not entries:
            return None

        values = [entry.value for entry in entries]
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)

        time_span = timedelta(0)
        if len(entries) > 1:
            time_span = entries[-1].timestamp - entries[0].timestamp

        return DataStatistics(
            min_value=min_val,
            max_value=max_val,
            avg_value=avg_val,
            latest_value=values[-1],
            sample_count=len(values),
            time_span=time_span,
        )

    def get_trend(self) -> str:
        """Determine trend direction based on recent values.

        Returns:
            "↑" for increasing, "→" for flat, "↓" for decreasing.
        """
        latest = self.buffer.get_latest(count=5)
        if len(latest) < 2:
            return "→"

        values = [entry.value for entry in latest]
        first = values[0]
        last = values[-1]

        # Consider 1% change threshold to avoid noise
        threshold = abs(first) * 0.01 if first != 0 else 0.01
        change = last - first

        if change > threshold:
            return "↑"
        elif change < -threshold:
            return "↓"
        else:
            return "→"

    def get_values_for_graph(self, count: Optional[int] = None) -> list:
        """Get values suitable for graphing.

        Args:
            count: Number of most recent values. If None, returns all.

        Returns:
            List of float values from oldest to newest.
        """
        if count:
            entries = self.buffer.get_latest(count)
        else:
            entries = self.buffer.get_all()

        return [entry.value for entry in entries]

    def clear(self) -> None:
        """Clear all historical data."""
        self.buffer.clear()

    def __len__(self) -> int:
        """Return number of readings in history."""
        return len(self.buffer)

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        trend = self.get_trend()
        if stats:
            return (
                f"SensorHistory(sensor={self.sensor_name}, readings={len(self)}, "
                f"trend={trend}, latest={stats.latest_value:.2f})"
            )
        return f"SensorHistory(sensor={self.sensor_name}, readings=0)"


class DataHistoryManager:
    """Manage historical data for multiple sensors."""

    def __init__(self, buffer_capacity: int = 120) -> None:
        """Initialize data history manager.

        Args:
            buffer_capacity: Size of circular buffer for each sensor.
        """
        self.buffer_capacity = buffer_capacity
        self._histories: Dict[str, SensorHistory] = {}

    def add_reading(
        self,
        sensor_name: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add a sensor reading to its history.

        Args:
            sensor_name: Name of the sensor.
            value: The sensor reading value.
            timestamp: Timestamp for the reading (uses current time if None).
        """
        if sensor_name not in self._histories:
            self._histories[sensor_name] = SensorHistory(
                sensor_name, self.buffer_capacity
            )

        self._histories[sensor_name].add_reading(value, timestamp)

    def get_history(self, sensor_name: str) -> Optional[SensorHistory]:
        """Get the history object for a sensor.

        Args:
            sensor_name: Name of the sensor.

        Returns:
            SensorHistory object or None if sensor not found.
        """
        return self._histories.get(sensor_name)

    def get_statistics(self, sensor_name: str) -> Optional[DataStatistics]:
        """Get statistics for a sensor.

        Args:
            sensor_name: Name of the sensor.

        Returns:
            DataStatistics object or None if sensor not found or no data.
        """
        history = self.get_history(sensor_name)
        if history:
            return history.get_statistics()
        return None

    def get_trend(self, sensor_name: str) -> str:
        """Get trend indicator for a sensor.

        Args:
            sensor_name: Name of the sensor.

        Returns:
            "↑" for increasing, "→" for flat, "↓" for decreasing, or "?" if no data.
        """
        history = self.get_history(sensor_name)
        if history:
            return history.get_trend()
        return "?"

    def get_all_sensors(self) -> Dict[str, SensorHistory]:
        """Get all tracked sensor histories.

        Returns:
            Dictionary of sensor name to SensorHistory.
        """
        return self._histories.copy()

    def clear(self) -> None:
        """Clear all historical data."""
        self._histories.clear()

    def __repr__(self) -> str:
        """String representation."""
        return f"DataHistoryManager(sensors={len(self._histories)})"
