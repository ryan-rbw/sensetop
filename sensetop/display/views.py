"""Display views for the TUI."""

import curses
from typing import TYPE_CHECKING, Callable, Optional

from sensetop.display.colors import ColorManager, ColorPair
from sensetop.display.graphs import GraphRenderer, create_trend_indicator
from sensetop.display.tui import UIView

if TYPE_CHECKING:
    from sensetop.app import SenseTopApp


class DashboardView(UIView):
    """Main dashboard view showing all sensor data."""

    def __init__(
        self,
        name: str,
        color_manager: ColorManager,
        app: "SenseTopApp",
    ) -> None:
        """Initialize dashboard view.

        Args:
            name: View name.
            color_manager: Color manager instance.
            app: Reference to main application.
        """
        super().__init__(name, color_manager)
        self.app = app

    def draw(self, stdscr: "curses._CursesWindow") -> None:
        """Draw the dashboard view.

        Args:
            stdscr: Curses window object.
        """
        try:
            height, width = stdscr.getmaxyx()

            # Draw header
            self._draw_header(stdscr, width)

            # Draw sensor sections
            self._draw_imu_section(stdscr, width, 3)
            self._draw_environmental_section(stdscr, width, 13)
            self._draw_system_section(stdscr, width, 23)

            # Draw footer
            self._draw_footer(stdscr, height, width)

        except curses.error:
            pass

    def _draw_header(self, stdscr: "curses._CursesWindow", width: int) -> None:
        """Draw the header section."""
        title = " SenseTop - Sensor Monitoring Dashboard "
        y = 0

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw title
        x = (width - len(title)) // 2
        stdscr.addstr(
            y + 1,
            x,
            title,
            self.color_manager.get_attr(ColorPair.HEADER),
        )

        # Draw border
        stdscr.addstr(
            y + 2,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

    def _draw_imu_section(self, stdscr: "curses._CursesWindow", width: int, start_y: int) -> None:
        """Draw IMU sensor data section."""
        # Section title
        stdscr.addstr(
            start_y,
            2,
            "IMU Sensor (9-DOF)",
            self.color_manager.get_attr(ColorPair.LABEL),
        )

        # Get IMU data if available
        imu_sensor = self.app.sensors.get("imu")
        if imu_sensor:
            try:
                reading = imu_sensor.read()
                imu_data = reading.value

                # Display accelerometer
                stdscr.addstr(
                    start_y + 1,
                    4,
                    f"Accel: X={imu_data.accel_x:6.2f}G  Y={imu_data.accel_y:6.2f}G  Z={imu_data.accel_z:6.2f}G",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

                # Display gyroscope
                stdscr.addstr(
                    start_y + 2,
                    4,
                    f"Gyro:  X={imu_data.gyro_x:7.1f}°/s  Y={imu_data.gyro_y:7.1f}°/s  Z={imu_data.gyro_z:7.1f}°/s",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

                # Display magnetometer
                stdscr.addstr(
                    start_y + 3,
                    4,
                    f"Mag:   X={imu_data.mag_x:6.2f}Gs  Y={imu_data.mag_y:6.2f}Gs  Z={imu_data.mag_z:6.2f}Gs",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

                # Display orientation
                stdscr.addstr(
                    start_y + 4,
                    4,
                    f"Orient: Pitch={imu_data.pitch:6.1f}°  Roll={imu_data.roll:6.1f}°  Yaw={imu_data.yaw:6.1f}°",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

            except Exception:
                stdscr.addstr(
                    start_y + 1,
                    4,
                    "Error reading IMU data",
                    self.color_manager.get_attr(ColorPair.STATUS_ERROR),
                )

    def _draw_environmental_section(
        self, stdscr: "curses._CursesWindow", width: int, start_y: int
    ) -> None:
        """Draw environmental sensor data section."""
        # Section title
        stdscr.addstr(
            start_y,
            2,
            "Environmental Sensors",
            self.color_manager.get_attr(ColorPair.LABEL),
        )

        # Get environmental data if available
        env_sensor = self.app.sensors.get("environmental")
        if env_sensor:
            try:
                reading = env_sensor.read()
                env_data = reading.value

                # Display temperature
                temp_color = self._get_temp_color(env_data.temperature)
                stdscr.addstr(
                    start_y + 1,
                    4,
                    f"Temperature:  {env_data.temperature:6.2f}°C",
                    self.color_manager.get_attr(temp_color),
                )

                # Display humidity
                humidity_color = self._get_humidity_color(env_data.humidity)
                stdscr.addstr(
                    start_y + 2,
                    4,
                    f"Humidity:     {env_data.humidity:6.2f}%",
                    self.color_manager.get_attr(humidity_color),
                )

                # Display pressure
                stdscr.addstr(
                    start_y + 3,
                    4,
                    f"Pressure:     {env_data.pressure:8.2f}hPa",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

                # Display dew point
                stdscr.addstr(
                    start_y + 4,
                    4,
                    f"Dew Point:    {env_data.dew_point:6.2f}°C",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

                # Display altitude
                stdscr.addstr(
                    start_y + 5,
                    4,
                    f"Altitude:     {env_data.altitude:8.2f}m",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

            except Exception:
                stdscr.addstr(
                    start_y + 1,
                    4,
                    "Error reading environmental data",
                    self.color_manager.get_attr(ColorPair.STATUS_ERROR),
                )

    def _draw_system_section(
        self, stdscr: "curses._CursesWindow", width: int, start_y: int
    ) -> None:
        """Draw system metrics section."""
        # Section title
        stdscr.addstr(
            start_y,
            2,
            "System Metrics",
            self.color_manager.get_attr(ColorPair.LABEL),
        )

        # Get system metrics if available
        sys_sensor = self.app.sensors.get("system")
        if sys_sensor:
            try:
                reading = sys_sensor.read()
                metrics = reading.value

                # Display CPU temperature
                cpu_color = self._get_cpu_temp_color(metrics.cpu_temp)
                stdscr.addstr(
                    start_y + 1,
                    4,
                    f"CPU Temp:     {metrics.cpu_temp:6.2f}°C",
                    self.color_manager.get_attr(cpu_color),
                )

                # Display memory usage
                mem_color = self._get_memory_color(metrics.memory_percent)
                mem_used_mb = metrics.memory_used // (1024 * 1024)
                mem_total_mb = metrics.memory_total // (1024 * 1024)
                stdscr.addstr(
                    start_y + 2,
                    4,
                    f"Memory:       {metrics.memory_percent:5.1f}% ({mem_used_mb}MB/{mem_total_mb}MB)",
                    self.color_manager.get_attr(mem_color),
                )

                # Display uptime
                uptime_hours = metrics.uptime.total_seconds() / 3600
                stdscr.addstr(
                    start_y + 3,
                    4,
                    f"Uptime:       {uptime_hours:7.1f} hours",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

                # Display CPU count
                stdscr.addstr(
                    start_y + 4,
                    4,
                    f"CPU Cores:    {metrics.cpu_count}",
                    self.color_manager.get_attr(ColorPair.VALUE),
                )

            except Exception:
                stdscr.addstr(
                    start_y + 1,
                    4,
                    "Error reading system metrics",
                    self.color_manager.get_attr(ColorPair.STATUS_ERROR),
                )

    def _draw_footer(self, stdscr: "curses._CursesWindow", height: int, width: int) -> None:
        """Draw the footer section."""
        footer = " q: Quit  h: Help  1-3: Views "
        y = height - 2

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw footer text
        x = (width - len(footer)) // 2
        stdscr.addstr(
            y + 1,
            x,
            footer,
            self.color_manager.get_attr(ColorPair.FOOTER),
        )

    @staticmethod
    def _get_temp_color(temp: float) -> ColorPair:
        """Get color for temperature value."""
        if temp < 0 or temp > 50:
            return ColorPair.STATUS_WARNING
        return ColorPair.STATUS_OK

    @staticmethod
    def _get_humidity_color(humidity: float) -> ColorPair:
        """Get color for humidity value."""
        if humidity < 30 or humidity > 70:
            return ColorPair.STATUS_WARNING
        return ColorPair.STATUS_OK

    @staticmethod
    def _get_cpu_temp_color(temp: float) -> ColorPair:
        """Get color for CPU temperature."""
        if temp > 80:
            return ColorPair.STATUS_CRITICAL
        if temp > 60:
            return ColorPair.STATUS_WARNING
        return ColorPair.STATUS_OK

    @staticmethod
    def _get_memory_color(percent: float) -> ColorPair:
        """Get color for memory usage percentage."""
        if percent > 90:
            return ColorPair.STATUS_CRITICAL
        if percent > 75:
            return ColorPair.STATUS_WARNING
        return ColorPair.STATUS_OK

    def handle_input(self, key: int) -> bool:
        """Handle keyboard input for dashboard view.

        Args:
            key: The keyboard key code.

        Returns:
            True if handled, False otherwise.
        """
        # Numeric keys for view switching are handled at TUI level
        # but we can handle view-specific shortcuts here
        if key == ord("r"):  # Refresh (already refreshing, but could force)
            return True
        return False


class HelpView(UIView):
    """Help view showing keyboard shortcuts and commands."""

    def __init__(self, name: str, color_manager: ColorManager) -> None:
        """Initialize help view.

        Args:
            name: View name.
            color_manager: Color manager instance.
        """
        super().__init__(name, color_manager)
        self.help_text = [
            " SenseTop - Keyboard Shortcuts & Help ",
            "",
            " Navigation ",
            "  1          Switch to Dashboard",
            "  2          Switch to Graphs (Historical Trends)",
            "  3          Switch to Alerts (Active Alarms)",
            "  4          Switch to Settings (Thresholds)",
            "",
            " General Controls ",
            "  h / ?      Show this help screen",
            "  q / ESC    Quit the application",
            "  r          Refresh current view",
            "",
            " Dashboard Controls ",
            "  (View updates automatically every 500ms)",
            "",
            " Graph Controls ",
            "  ↑/↓ or j/k  Navigate between graphs",
            "",
            " Alert Controls ",
            "  a          Acknowledge all active alarms",
            "",
            " Settings Controls ",
            "  ↑/↓ or j/k  Select sensor threshold",
            "  r          Reset all to defaults",
            "",
            " Display Indicators ",
            "  [OK]       Status is normal",
            "  [WARNING]  Values approaching limits",
            "  [CRITICAL] Values exceed safe thresholds",
            "  ↑          Trending upward",
            "  →          Flat/stable",
            "  ↓          Trending downward",
            "",
            " Alarm Severity ",
            "  🟡 WARNING  Alert within warning range",
            "  🔴 CRITICAL Alert within critical range",
            "",
            " Project Information ",
            "  GitHub: https://github.com/ryan-rbw/sensetop",
            "  Version: 0.1.0-dev",
            "",
            " Press any key to return to dashboard ",
        ]

    def draw(self, stdscr: "curses._CursesWindow") -> None:
        """Draw the help view.

        Args:
            stdscr: Curses window object.
        """
        if stdscr is None:
            return

        try:
            height, width = stdscr.getmaxyx()

            # Draw border and title
            self._draw_header(stdscr, width)

            # Draw help text
            for i, line in enumerate(self.help_text):
                if i + 3 >= height - 1:
                    break  # Stop if we run out of space

                if line.startswith(" ") and line.endswith(" "):
                    # Section headers
                    attr = self.color_manager.get_attr(ColorPair.HEADER)
                else:
                    attr = self.color_manager.get_attr(ColorPair.VALUE)

                try:
                    stdscr.addstr(i + 3, 2, line[: width - 4], attr)
                except curses.error:
                    pass

            # Draw footer
            self._draw_footer(stdscr, height, width)

        except curses.error:
            pass

    def _draw_header(self, stdscr: "curses._CursesWindow", width: int) -> None:
        """Draw the header section."""
        title = " SenseTop - Help "
        y = 0

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw title
        x = (width - len(title)) // 2
        stdscr.addstr(
            y + 1,
            x,
            title,
            self.color_manager.get_attr(ColorPair.HEADER),
        )

        # Draw border
        stdscr.addstr(
            y + 2,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

    def _draw_footer(self, stdscr: "curses._CursesWindow", height: int, width: int) -> None:
        """Draw the footer section."""
        footer = " Press any key to return to dashboard "
        y = height - 2

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw footer text
        x = (width - len(footer)) // 2
        stdscr.addstr(
            y + 1,
            x,
            footer,
            self.color_manager.get_attr(ColorPair.FOOTER),
        )

    def handle_input(self, key: int) -> bool:
        """Handle keyboard input for help view.

        Args:
            key: The keyboard key code.

        Returns:
            True if handled, False otherwise.
        """
        # Any key returns to dashboard
        if key != -1:
            # Signal to return to dashboard (handled by app)
            return False
        return True


class GraphView(UIView):
    """View showing historical data trends and sparklines."""

    def __init__(
        self,
        name: str,
        color_manager: ColorManager,
        app: "SenseTopApp",
    ) -> None:
        """Initialize graph view.

        Args:
            name: View name.
            color_manager: Color manager instance.
            app: Reference to main application.
        """
        super().__init__(name, color_manager)
        self.app = app
        self.selected_graph = 0  # Currently selected sensor graph

    def draw(self, stdscr: "curses._CursesWindow") -> None:
        """Draw the graph view with trend sparklines.

        Args:
            stdscr: Curses window object.
        """
        if stdscr is None:
            return

        try:
            height, width = stdscr.getmaxyx()

            # Draw header
            self._draw_header(stdscr, width)

            # Draw graph section
            self._draw_graphs(stdscr, width, height, start_y=3)

            # Draw footer
            self._draw_footer(stdscr, height, width)

        except curses.error:
            pass

    def _draw_header(self, stdscr: "curses._CursesWindow", width: int) -> None:
        """Draw the header section."""
        title = " SenseTop - Historical Trends "
        y = 0

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw title
        x = (width - len(title)) // 2
        stdscr.addstr(
            y + 1,
            x,
            title,
            self.color_manager.get_attr(ColorPair.HEADER),
        )

        # Draw border
        stdscr.addstr(
            y + 2,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

    def _draw_graphs(
        self,
        stdscr: "curses._CursesWindow",
        width: int,
        height: int,
        start_y: int,
    ) -> None:
        """Draw sparkline graphs for each sensor type."""
        if not hasattr(self.app, "data_history"):
            # Data history not yet initialized
            stdscr.addstr(
                start_y + 1,
                2,
                "No historical data available yet",
                self.color_manager.get_attr(ColorPair.VALUE),
            )
            return

        y = start_y
        sensors_data = [
            ("Temperature", "temperature"),
            ("Humidity", "humidity"),
            ("Pressure", "pressure"),
            ("CPU Temp", "cpu_temperature"),
        ]

        # Calculate chart height based on available space
        available_height = height - start_y - 3  # Leave room for footer
        chart_height = max(3, min(5, available_height // len(sensors_data) - 2))

        for label, sensor_name in sensors_data:
            if y + chart_height + 3 >= height - 2:
                break

            history = self.app.data_history.get_history(sensor_name)
            if history and len(history) > 0:
                stats = history.get_statistics()
                trend = history.get_trend()
                values = history.get_values_for_graph(count=width - 20)

                # Draw sensor label with trend
                trend_str = create_trend_indicator(trend)
                label_str = f"{label:12} {trend_str}"
                stats_str = (
                    f"Latest: {stats.latest_value:7.2f}  "
                    f"Min: {stats.min_value:7.2f}  "
                    f"Max: {stats.max_value:7.2f}"
                )

                # Draw label and stats
                try:
                    stdscr.addstr(
                        y,
                        2,
                        label_str,
                        self.color_manager.get_attr(ColorPair.LABEL),
                    )
                    stdscr.addstr(
                        y,
                        len(label_str) + 2,
                        stats_str[: width - len(label_str) - 4],
                        self.color_manager.get_attr(ColorPair.VALUE),
                    )

                    # Draw bar chart (multi-line graph)
                    bar_chart = GraphRenderer.render_bar_chart(
                        values,
                        height=chart_height,
                        width=width - 4
                    )
                    chart_lines = bar_chart.split('\n')
                    for i, line in enumerate(chart_lines):
                        if y + 1 + i < height - 2:
                            stdscr.addstr(
                                y + 1 + i,
                                2,
                                line,
                                self.color_manager.get_attr(ColorPair.VALUE),
                            )

                except curses.error:
                    pass

                y += chart_height + 2  # Height of chart + spacing

    def _draw_footer(self, stdscr: "curses._CursesWindow", height: int, width: int) -> None:
        """Draw the footer section."""
        footer = " ↑↓: Select  Enter: Details  1: Dashboard  q: Quit "
        y = height - 2

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw footer text
        x = max(0, (width - len(footer)) // 2)
        footer_text = footer[: width - 2]
        stdscr.addstr(
            y + 1,
            max(1, x),
            footer_text,
            self.color_manager.get_attr(ColorPair.FOOTER),
        )

    def handle_input(self, key: int) -> bool:
        """Handle keyboard input for graph view.

        Args:
            key: The keyboard key code.

        Returns:
            True if handled, False otherwise.
        """
        # Arrow keys for navigation (if needed)
        if key == curses.KEY_UP or key == ord("k"):
            self.selected_graph = max(0, self.selected_graph - 1)
            return True
        elif key == curses.KEY_DOWN or key == ord("j"):
            self.selected_graph += 1
            return True

        # Return to dashboard on unsupported keys
        if key != -1 and key not in [ord("k"), ord("j")]:
            return False


class AlertView(UIView):
    """View for displaying active and critical alarms."""

    def __init__(
        self,
        name: str,
        color_manager: ColorManager,
        app: "SenseTopApp",
    ) -> None:
        """Initialize alert view.

        Args:
            name: View name.
            color_manager: Color manager instance.
            app: Reference to main application.
        """
        super().__init__(name, color_manager)
        self.app = app

    def draw(self, stdscr: "curses._CursesWindow") -> None:
        """Draw the alert view.

        Args:
            stdscr: Curses window object.
        """
        if stdscr is None:
            return

        try:
            height, width = stdscr.getmaxyx()

            # Draw header
            self._draw_header(stdscr, width)

            # Get active alarms from alarm manager
            active_alarms = self.app.alarm_manager.get_active_alarms()
            critical_alarms = self.app.alarm_manager.get_active_critical_alarms()

            # Draw alarm summary
            self._draw_summary(stdscr, width, 3, active_alarms, critical_alarms)

            # Draw active alarms list
            self._draw_alarms_list(stdscr, width, height, active_alarms)

            # Draw footer
            self._draw_footer(stdscr, height, width)

        except curses.error:
            pass

    def _draw_header(self, stdscr: "curses._CursesWindow", width: int) -> None:
        """Draw the header section."""
        title = " SenseTop - Active Alarms "
        y = 0

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw title
        x = (width - len(title)) // 2
        stdscr.addstr(
            y + 1,
            x,
            title,
            self.color_manager.get_attr(ColorPair.HEADER),
        )

        # Draw border
        stdscr.addstr(
            y + 2,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

    def _draw_summary(
        self,
        stdscr: "curses._CursesWindow",
        width: int,
        y: int,
        active_alarms: list,
        critical_alarms: list,
    ) -> None:
        """Draw alarm summary statistics.

        Args:
            stdscr: Curses window object.
            width: Screen width.
            y: Y position to start drawing.
            active_alarms: List of active alarm events.
            critical_alarms: List of critical alarm events.
        """
        # Count warnings (active but not critical)
        warnings = len(active_alarms) - len(critical_alarms)

        # Draw summary line
        summary = (
            f"Total: {len(active_alarms)} | Critical: {len(critical_alarms)} | Warnings: {warnings}"
        )
        try:
            stdscr.addstr(
                y,
                2,
                summary,
                self.color_manager.get_attr(ColorPair.HEADER),
            )
        except curses.error:
            pass

    def _draw_alarms_list(
        self,
        stdscr: "curses._CursesWindow",
        width: int,
        height: int,
        active_alarms: list,
    ) -> None:
        """Draw the list of active alarms.

        Args:
            stdscr: Curses window object.
            width: Screen width.
            height: Screen height.
            active_alarms: List of active alarm events.
        """
        y = 5

        if not active_alarms:
            # Draw "no alarms" message
            message = " ✓ No active alarms "
            try:
                stdscr.addstr(
                    y,
                    (width - len(message)) // 2,
                    message,
                    self.color_manager.get_attr(ColorPair.VALUE),
                )
            except curses.error:
                pass
            return

        # Draw each alarm
        for i, alarm in enumerate(active_alarms):
            if y + i >= height - 3:
                break  # Stop if we run out of space

            # Format alarm line
            ack_marker = "✓" if alarm.acknowledged else " "
            severity_marker = "🔴" if alarm.severity.value == "critical" else "🟡"

            # Truncate message to fit width
            sensor_info = f"{severity_marker} [{alarm.severity.value.upper():8}] {alarm.sensor_name}: {alarm.value:.2f}"

            # Choose color based on severity and acknowledgment
            if alarm.acknowledged:
                attr = self.color_manager.get_attr(ColorPair.VALUE)
            elif alarm.severity.value == "critical":
                attr = self.color_manager.get_attr(ColorPair.STATUS_ERROR)
            else:
                attr = self.color_manager.get_attr(ColorPair.STATUS_WARNING)

            try:
                display_text = sensor_info[: width - 4]
                stdscr.addstr(y + i, 2, f"{ack_marker} {display_text}", attr)
            except curses.error:
                pass

    def _draw_footer(self, stdscr: "curses._CursesWindow", height: int, width: int) -> None:
        """Draw the footer section.

        Args:
            stdscr: Curses window object.
            height: Screen height.
            width: Screen width.
        """
        footer = " a: Acknowledge All  1: Dashboard  q: Quit "
        y = height - 2

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw footer text
        x = max(0, (width - len(footer)) // 2)
        footer_text = footer[: width - 2]
        try:
            stdscr.addstr(
                y + 1,
                max(1, x),
                footer_text,
                self.color_manager.get_attr(ColorPair.FOOTER),
            )
        except curses.error:
            pass

    def handle_input(self, key: int) -> bool:
        """Handle keyboard input for alert view.

        Args:
            key: The keyboard key code.

        Returns:
            True if handled, False otherwise.
        """
        # Acknowledge all alarms
        if key == ord("a"):
            self.app.alarm_manager.acknowledge_all()
            return True

        # Any other key returns False (will be handled by main loop)
        return False


class SettingsView(UIView):
    """View for configuring thresholds and application settings."""

    def __init__(
        self,
        name: str,
        color_manager: ColorManager,
        app: "SenseTopApp",
    ) -> None:
        """Initialize settings view.

        Args:
            name: View name.
            color_manager: Color manager instance.
            app: Reference to main application.
        """
        super().__init__(name, color_manager)
        self.app = app
        self.selected_sensor_idx = 0

    def draw(self, stdscr: "curses._CursesWindow") -> None:
        """Draw the settings view.

        Args:
            stdscr: Curses window object.
        """
        if stdscr is None:
            return

        try:
            height, width = stdscr.getmaxyx()

            # Draw header
            self._draw_header(stdscr, width)

            # Get list of sensors with thresholds
            thresholds = self.app.threshold_manager.get_all_thresholds()
            sensor_names = list(thresholds.keys())

            # Draw sensor list with selection
            self._draw_sensor_list(stdscr, width, sensor_names)

            # Draw details for selected sensor
            if sensor_names:
                selected_sensor = sensor_names[self.selected_sensor_idx % len(sensor_names)]
                self._draw_threshold_details(
                    stdscr, width, selected_sensor, thresholds[selected_sensor]
                )

            # Draw footer
            self._draw_footer(stdscr, height, width)

        except curses.error:
            pass

    def _draw_header(self, stdscr: "curses._CursesWindow", width: int) -> None:
        """Draw the header section."""
        title = " SenseTop - Settings & Thresholds "
        y = 0

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw title
        x = (width - len(title)) // 2
        stdscr.addstr(
            y + 1,
            x,
            title,
            self.color_manager.get_attr(ColorPair.HEADER),
        )

        # Draw border
        stdscr.addstr(
            y + 2,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

    def _draw_sensor_list(
        self,
        stdscr: "curses._CursesWindow",
        width: int,
        sensor_names: list,
    ) -> None:
        """Draw the list of sensors.

        Args:
            stdscr: Curses window object.
            width: Screen width.
            sensor_names: List of sensor names.
        """
        y = 4
        list_title = " Sensors "
        try:
            stdscr.addstr(
                y,
                2,
                list_title,
                self.color_manager.get_attr(ColorPair.HEADER),
            )
        except curses.error:
            pass

        for i, sensor_name in enumerate(sensor_names):
            if y + i + 1 >= 18:
                break

            # Highlight selected sensor
            if i == (self.selected_sensor_idx % len(sensor_names)):
                attr = self.color_manager.get_attr(ColorPair.ERROR)
                marker = "▶"
            else:
                attr = self.color_manager.get_attr(ColorPair.VALUE)
                marker = " "

            try:
                display_text = f"{marker} {sensor_name}"[: width - 4]
                stdscr.addstr(y + i + 1, 4, display_text, attr)
            except curses.error:
                pass

    def _draw_threshold_details(
        self,
        stdscr: "curses._CursesWindow",
        width: int,
        sensor_name: str,
        threshold,
    ) -> None:
        """Draw threshold details for the selected sensor.

        Args:
            stdscr: Curses window object.
            width: Screen width.
            sensor_name: Name of the selected sensor.
            threshold: SensorThreshold object.
        """
        y = 4
        x = 30

        # Draw section title
        title = f" {sensor_name.upper()} Thresholds "
        try:
            stdscr.addstr(
                y,
                x,
                title,
                self.color_manager.get_attr(ColorPair.HEADER),
            )
        except curses.error:
            pass

        # Draw threshold details
        details = [
            f"Enabled: {'Yes' if threshold.enabled else 'No'}",
            f"Warning Min: {threshold.min_value:.2f}",
            f"Warning Max: {threshold.max_value:.2f}",
            f"Critical Min: {threshold.critical_min if threshold.critical_min is not None else 'N/A'}",
            f"Critical Max: {threshold.critical_max if threshold.critical_max is not None else 'N/A'}",
        ]

        for i, detail in enumerate(details):
            if y + i + 1 >= 18:
                break
            try:
                display_text = detail[: width - x - 2]
                stdscr.addstr(
                    y + i + 1,
                    x + 2,
                    display_text,
                    self.color_manager.get_attr(ColorPair.VALUE),
                )
            except curses.error:
                pass

    def _draw_footer(self, stdscr: "curses._CursesWindow", height: int, width: int) -> None:
        """Draw the footer section.

        Args:
            stdscr: Curses window object.
            height: Screen height.
            width: Screen width.
        """
        footer = " ↑↓: Select  r: Reset to Defaults  1: Dashboard  q: Quit "
        y = height - 2

        # Draw border
        stdscr.addstr(
            y,
            0,
            "═" * width,
            self.color_manager.get_attr(ColorPair.BORDER),
        )

        # Draw footer text
        x = max(0, (width - len(footer)) // 2)
        footer_text = footer[: width - 2]
        try:
            stdscr.addstr(
                y + 1,
                max(1, x),
                footer_text,
                self.color_manager.get_attr(ColorPair.FOOTER),
            )
        except curses.error:
            pass

    def handle_input(self, key: int) -> bool:
        """Handle keyboard input for settings view.

        Args:
            key: The keyboard key code.

        Returns:
            True if handled, False otherwise.
        """
        thresholds = self.app.threshold_manager.get_all_thresholds()
        num_sensors = len(thresholds)

        if num_sensors == 0:
            return False

        # Navigate sensors
        if key == curses.KEY_UP or key == ord("k"):
            self.selected_sensor_idx = (self.selected_sensor_idx - 1) % num_sensors
            return True
        elif key == curses.KEY_DOWN or key == ord("j"):
            self.selected_sensor_idx = (self.selected_sensor_idx + 1) % num_sensors
            return True

        # Reset to defaults
        elif key == ord("r"):
            self.app.threshold_manager.reset_to_defaults()
            self.selected_sensor_idx = 0
            return True

        # Any other key returns False (will be handled by main loop)
        return False
