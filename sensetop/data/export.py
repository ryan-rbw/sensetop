"""Data export functionality for historical sensor data."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from sensetop.data.history import DataHistoryManager, SensorHistory


class DataExporter:
    """Export sensor data to various formats."""

    def __init__(self, output_dir: Optional[str] = None) -> None:
        """Initialize data exporter.

        Args:
            output_dir: Directory to write exported files.
                       If None, uses ~/.sensetop/exports/
        """
        if output_dir is None:
            output_dir = str(Path.home() / ".sensetop" / "exports")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_csv(
        self,
        history: SensorHistory,
        sensor_name: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """Export sensor history to CSV file.

        Args:
            history: SensorHistory object to export.
            sensor_name: Sensor name (used in filename if provided).
            filename: Custom filename. If None, generates from sensor name.

        Returns:
            Path to the exported CSV file.

        Raises:
            IOError: If file cannot be written.
        """
        if filename is None:
            if sensor_name is None:
                sensor_name = history.sensor_name

            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{sensor_name}_{timestamp}.csv"

        filepath = self.output_dir / filename

        # Get all entries from history
        entries = history.buffer.get_all()

        if not entries:
            raise ValueError("No data to export")

        # Write CSV file
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow(["timestamp", "value"])

                # Write data rows
                for entry in entries:
                    writer.writerow([entry.timestamp.isoformat(), f"{entry.value:.4f}"])

            return filepath

        except IOError as e:
            raise IOError(f"Failed to write CSV file {filepath}: {e}") from e

    def export_all_to_csv(
        self,
        manager: DataHistoryManager,
        suffix: Optional[str] = None,
    ) -> dict:
        """Export all sensor histories to separate CSV files.

        Args:
            manager: DataHistoryManager containing all sensor histories.
            suffix: Optional suffix to add to all filenames.

        Returns:
            Dictionary mapping sensor names to exported file paths.

        Raises:
            IOError: If any file cannot be written.
        """
        results = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for sensor_name, history in manager.get_all_sensors().items():
            try:
                # Generate filename with timestamp
                filename = f"{sensor_name}_{timestamp}"
                if suffix:
                    filename += f"_{suffix}"
                filename += ".csv"

                filepath = self.export_to_csv(history, sensor_name, filename)
                results[sensor_name] = filepath

            except ValueError:
                # Skip sensors with no data
                continue

        if not results:
            raise ValueError("No sensor data to export")

        return results

    def export_summary_csv(
        self,
        manager: DataHistoryManager,
        filename: Optional[str] = None,
    ) -> Path:
        """Export summary statistics for all sensors to CSV.

        Args:
            manager: DataHistoryManager containing all sensor histories.
            filename: Custom filename. If None, generates default.

        Returns:
            Path to the exported CSV file.

        Raises:
            IOError: If file cannot be written.
            ValueError: If no data to export.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.csv"

        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow(
                    [
                        "sensor",
                        "samples",
                        "latest",
                        "min",
                        "max",
                        "average",
                        "time_span",
                    ]
                )

                # Write summary for each sensor
                data_written = False
                for sensor_name, history in manager.get_all_sensors().items():
                    stats = history.get_statistics()
                    if stats:
                        data_written = True
                        time_span_str = str(stats.time_span).split(".")[0]  # Format timedelta
                        writer.writerow(
                            [
                                sensor_name,
                                stats.sample_count,
                                f"{stats.latest_value:.4f}",
                                f"{stats.min_value:.4f}",
                                f"{stats.max_value:.4f}",
                                f"{stats.avg_value:.4f}",
                                time_span_str,
                            ]
                        )

                if not data_written:
                    raise ValueError("No sensor data to export")

            return filepath

        except IOError as e:
            raise IOError(f"Failed to write CSV file {filepath}: {e}") from e

    def get_export_directory(self) -> Path:
        """Get the export directory path."""
        return self.output_dir

    def list_exports(self) -> list:
        """List all exported files in the export directory.

        Returns:
            List of CSV file paths in the export directory.
        """
        return sorted(self.output_dir.glob("*.csv"))

    def __repr__(self) -> str:
        """String representation."""
        return f"DataExporter(output_dir={self.output_dir})"
