"""Display views for the TUI."""

import curses
from typing import TYPE_CHECKING, Callable, Optional

from sensetop.display.colors import ColorManager, ColorPair
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

    def _draw_imu_section(
        self, stdscr: "curses._CursesWindow", width: int, start_y: int
    ) -> None:
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

    def _draw_footer(
        self, stdscr: "curses._CursesWindow", height: int, width: int
    ) -> None:
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
            "  2          Switch to Settings (TODO)",
            "  3          Switch to About (TODO)",
            "",
            " General Controls ",
            "  h / ?      Show this help screen",
            "  q / ESC    Quit the application",
            "  r          Refresh current view",
            "",
            " Dashboard Controls ",
            "  (View updates automatically every 500ms)",
            "",
            " Display Indicators ",
            "  [OK]       Status is normal",
            "  [WARNING]  Values approaching limits",
            "  [CRITICAL] Values exceed safe thresholds",
            "",
            " Thresholds ",
            "  Temperature:    0-50°C (OK), outside = WARNING",
            "  Humidity:       30-70% (OK), outside = WARNING",
            "  CPU Temp:       <60°C (OK), 60-80°C (WARN), >80°C (CRIT)",
            "  Memory Usage:   <75% (OK), 75-90% (WARN), >90% (CRIT)",
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

    def _draw_footer(
        self, stdscr: "curses._CursesWindow", height: int, width: int
    ) -> None:
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
