"""Unit tests for data processing and storage modules."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from sensetop.data.buffer import BufferEntry, CircularBuffer
from sensetop.data.export import DataExporter
from sensetop.data.history import DataHistoryManager, SensorHistory
from sensetop.display.graphs import GraphRenderer


class TestCircularBuffer:
    """Tests for circular buffer implementation."""

    def test_buffer_creation(self):
        """Test buffer initialization."""
        buf = CircularBuffer(capacity=10)
        assert buf.capacity == 10
        assert len(buf) == 0
        assert buf.is_empty()

    def test_buffer_append(self):
        """Test appending values to buffer."""
        buf = CircularBuffer(capacity=5)
        buf.append(1.0)
        buf.append(2.0)
        assert len(buf) == 2

    def test_buffer_full(self):
        """Test buffer full condition."""
        buf = CircularBuffer(capacity=3)
        assert not buf.is_full()
        buf.append(1.0)
        buf.append(2.0)
        buf.append(3.0)
        assert buf.is_full()
        assert len(buf) == 3

    def test_buffer_overflow(self):
        """Test buffer overwrites oldest when full."""
        buf = CircularBuffer(capacity=3)
        buf.append(1.0)
        buf.append(2.0)
        buf.append(3.0)
        buf.append(4.0)  # Should overwrite 1.0

        values = [e.value for e in buf.get_all()]
        assert values == [2.0, 3.0, 4.0]

    def test_buffer_get_all(self):
        """Test retrieving all entries in order."""
        buf = CircularBuffer(capacity=5)
        for i in range(3):
            buf.append(float(i))

        entries = buf.get_all()
        assert len(entries) == 3
        assert [e.value for e in entries] == [0.0, 1.0, 2.0]

    def test_buffer_get_latest(self):
        """Test retrieving most recent entries."""
        buf = CircularBuffer(capacity=10)
        for i in range(5):
            buf.append(float(i))

        latest = buf.get_latest(count=3)
        assert len(latest) == 3
        assert [e.value for e in latest] == [2.0, 3.0, 4.0]

    def test_buffer_get_oldest(self):
        """Test retrieving oldest entries."""
        buf = CircularBuffer(capacity=10)
        for i in range(5):
            buf.append(float(i))

        oldest = buf.get_oldest(count=2)
        assert len(oldest) == 2
        assert [e.value for e in oldest] == [0.0, 1.0]

    def test_buffer_clear(self):
        """Test clearing buffer."""
        buf = CircularBuffer(capacity=5)
        buf.append(1.0)
        buf.append(2.0)
        assert len(buf) == 2

        buf.clear()
        assert len(buf) == 0
        assert buf.is_empty()

    def test_buffer_timestamps(self):
        """Test timestamp handling."""
        buf = CircularBuffer(capacity=5)
        ts1 = datetime.now()
        buf.append(1.0, ts1)
        ts2 = datetime.now()
        buf.append(2.0, ts2)

        entries = buf.get_all()
        assert entries[0].timestamp == ts1
        assert entries[1].timestamp == ts2

    def test_buffer_invalid_capacity(self):
        """Test buffer rejects invalid capacity."""
        with pytest.raises(ValueError):
            CircularBuffer(capacity=0)

        with pytest.raises(ValueError):
            CircularBuffer(capacity=-1)


class TestSensorHistory:
    """Tests for sensor history tracking."""

    def test_history_creation(self):
        """Test history object initialization."""
        hist = SensorHistory("temperature")
        assert hist.sensor_name == "temperature"
        assert len(hist) == 0

    def test_history_add_reading(self):
        """Test adding sensor readings."""
        hist = SensorHistory("temperature")
        hist.add_reading(20.5)
        hist.add_reading(21.0)
        assert len(hist) == 2

    def test_history_statistics(self):
        """Test statistics calculation."""
        hist = SensorHistory("temperature")
        hist.add_reading(20.0)
        hist.add_reading(30.0)
        hist.add_reading(25.0)

        stats = hist.get_statistics()
        assert stats is not None
        assert stats.min_value == 20.0
        assert stats.max_value == 30.0
        assert stats.avg_value == 25.0
        assert stats.latest_value == 25.0
        assert stats.sample_count == 3

    def test_history_trend_rising(self):
        """Test trend detection for rising values."""
        hist = SensorHistory("temperature")
        for i in range(10):
            hist.add_reading(float(i * 10))  # 0, 10, 20, ..., 90

        trend = hist.get_trend()
        assert trend == "↑"

    def test_history_trend_falling(self):
        """Test trend detection for falling values."""
        hist = SensorHistory("temperature")
        for i in range(10):
            hist.add_reading(float(100 - i * 10))  # 100, 90, 80, ..., 10

        trend = hist.get_trend()
        assert trend == "↓"

    def test_history_trend_flat(self):
        """Test trend detection for flat values."""
        hist = SensorHistory("temperature")
        for i in range(5):
            hist.add_reading(25.0)  # All same value

        trend = hist.get_trend()
        assert trend == "→"

    def test_history_empty_statistics(self):
        """Test statistics with empty history."""
        hist = SensorHistory("temperature")
        stats = hist.get_statistics()
        assert stats is None

    def test_history_values_for_graph(self):
        """Test getting values for graphing."""
        hist = SensorHistory("humidity")
        for i in range(5):
            hist.add_reading(float(50 + i))

        values = hist.get_values_for_graph()
        assert values == [50.0, 51.0, 52.0, 53.0, 54.0]

        # Test with count limit
        values_limited = hist.get_values_for_graph(count=2)
        assert values_limited == [53.0, 54.0]


class TestDataHistoryManager:
    """Tests for multi-sensor data history management."""

    def test_manager_creation(self):
        """Test manager initialization."""
        manager = DataHistoryManager()
        assert len(manager.get_all_sensors()) == 0

    def test_manager_add_reading(self):
        """Test adding readings to multiple sensors."""
        manager = DataHistoryManager()
        manager.add_reading("temperature", 20.0)
        manager.add_reading("humidity", 50.0)
        manager.add_reading("temperature", 21.0)

        assert len(manager.get_all_sensors()) == 2
        temp_hist = manager.get_history("temperature")
        assert len(temp_hist) == 2

    def test_manager_get_statistics(self):
        """Test getting statistics from manager."""
        manager = DataHistoryManager()
        manager.add_reading("temperature", 20.0)
        manager.add_reading("temperature", 30.0)

        stats = manager.get_statistics("temperature")
        assert stats is not None
        assert stats.min_value == 20.0
        assert stats.max_value == 30.0

    def test_manager_get_trend(self):
        """Test getting trend from manager."""
        manager = DataHistoryManager()
        for i in range(5):
            manager.add_reading("temperature", float(i * 10))

        trend = manager.get_trend("temperature")
        assert trend == "↑"

    def test_manager_nonexistent_sensor(self):
        """Test accessing nonexistent sensor."""
        manager = DataHistoryManager()
        assert manager.get_history("nonexistent") is None
        assert manager.get_statistics("nonexistent") is None
        assert manager.get_trend("nonexistent") == "?"

    def test_manager_clear(self):
        """Test clearing all data."""
        manager = DataHistoryManager()
        manager.add_reading("temperature", 20.0)
        manager.add_reading("humidity", 50.0)

        manager.clear()
        assert len(manager.get_all_sensors()) == 0


class TestDataExporter:
    """Tests for data export functionality."""

    def test_exporter_creation(self):
        """Test exporter initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = DataExporter(output_dir=tmpdir)
            assert exporter.output_dir == Path(tmpdir)

    def test_export_to_csv(self):
        """Test exporting sensor history to CSV."""
        hist = SensorHistory("temperature")
        for i in range(3):
            hist.add_reading(float(20 + i))

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = DataExporter(output_dir=tmpdir)
            filepath = exporter.export_to_csv(hist, sensor_name="temperature")

            assert filepath.exists()
            assert filepath.suffix == ".csv"

            # Verify CSV content
            with open(filepath) as f:
                lines = f.readlines()
                assert len(lines) == 4  # Header + 3 data rows
                assert "timestamp,value" in lines[0]

    def test_export_all_to_csv(self):
        """Test exporting all sensor histories."""
        manager = DataHistoryManager()
        manager.add_reading("temperature", 20.0)
        manager.add_reading("temperature", 21.0)
        manager.add_reading("humidity", 50.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = DataExporter(output_dir=tmpdir)
            results = exporter.export_all_to_csv(manager)

            assert len(results) == 2
            assert "temperature" in results
            assert "humidity" in results

    def test_export_summary_csv(self):
        """Test exporting summary statistics."""
        manager = DataHistoryManager()
        for i in range(5):
            manager.add_reading("temperature", float(20 + i))

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = DataExporter(output_dir=tmpdir)
            filepath = exporter.export_summary_csv(manager)

            assert filepath.exists()
            with open(filepath) as f:
                lines = f.readlines()
                assert "sensor,samples" in lines[0]
                assert "temperature" in lines[1]

    def test_export_empty_history(self):
        """Test exporting empty history raises error."""
        hist = SensorHistory("temperature")
        exporter = DataExporter()

        with pytest.raises(ValueError):
            exporter.export_to_csv(hist)

    def test_list_exports(self):
        """Test listing exported files."""
        hist = SensorHistory("temperature")
        hist.add_reading(20.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = DataExporter(output_dir=tmpdir)
            exporter.export_to_csv(hist, sensor_name="temperature")

            exports = exporter.list_exports()
            assert len(exports) == 1


class TestGraphRenderer:
    """Tests for graph rendering functionality."""

    def test_sparkline_basic(self):
        """Test basic sparkline rendering."""
        values = [1.0, 2.0, 3.0, 2.0, 1.0]
        sparkline = GraphRenderer.render_sparkline(values)

        assert len(sparkline) == 5
        assert all(c in GraphRenderer.SPARKLINE_CHARS for c in sparkline)

    def test_sparkline_constant_values(self):
        """Test sparkline with constant values."""
        values = [5.0, 5.0, 5.0, 5.0]
        sparkline = GraphRenderer.render_sparkline(values)

        assert len(sparkline) == 4
        # Constant values should produce consistent character (not necessarily max)
        assert all(c in GraphRenderer.SPARKLINE_CHARS for c in sparkline)

    def test_sparkline_empty(self):
        """Test sparkline with empty values."""
        sparkline = GraphRenderer.render_sparkline([])
        assert sparkline == ""

    def test_bar_chart_rendering(self):
        """Test bar chart rendering."""
        values = [1.0, 5.0, 3.0, 4.0, 2.0]
        chart = GraphRenderer.render_bar_chart(values, height=3, width=5)

        lines = chart.split("\n")
        assert len(lines) == 3  # height (one line per height unit)
        assert all(len(line) == 5 for line in lines)  # width check

    def test_line_graph_rendering(self):
        """Test line graph rendering."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        graph = GraphRenderer.render_line_graph(values, height=5, width=5)

        lines = graph.split("\n")
        assert len(lines) == 5

    def test_mini_graph_sparkline(self):
        """Test mini graph in sparkline mode."""
        values = [1.0, 2.0, 3.0, 2.0, 1.0]
        graph = GraphRenderer.render_mini_graph(values, mode="sparkline")

        assert len(graph) > 0

    def test_trend_indicator(self):
        """Test trend indicator formatting."""
        from sensetop.display.graphs import create_trend_indicator

        assert create_trend_indicator("↑") == " ↑ "
        assert create_trend_indicator("→") == " → "
        assert create_trend_indicator("↓") == " ↓ "
        assert create_trend_indicator("?") == " ? "

    def test_format_value_with_range(self):
        """Test value formatting with range position."""
        formatted, position = GraphRenderer.format_value_with_range(10.0, 0.0, 100.0)

        assert formatted == "10.00"
        assert position == "◄"

        formatted, position = GraphRenderer.format_value_with_range(50.0, 0.0, 100.0)
        assert position == "■"

        formatted, position = GraphRenderer.format_value_with_range(90.0, 0.0, 100.0)
        assert position == "►"
