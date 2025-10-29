"""Main SenseTop application class."""

import curses
import logging
import threading
import time
from typing import Dict, List, Optional

from sensetop.config import Config
from sensetop.data.alarms import AlarmManager
from sensetop.data.history import DataHistoryManager
from sensetop.data.thresholds import ThresholdManager
from sensetop.display.colors import ColorManager, ColorScheme
from sensetop.display.tui import TUI
from sensetop.display.views import AlertView, DashboardView, GraphView, HelpView, SettingsView
from sensetop.sensors.environmental import EnvironmentalSensor
from sensetop.sensors.imu import IMUSensor
from sensetop.sensors.system import SystemSensor


class SenseTopApp:
    """Main SenseTop application class.

    Manages the application lifecycle, sensor data collection, and UI rendering.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize the SenseTop application.

        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.logger = self._setup_logging()
        self.logger.info("Initializing SenseTop application")

        # UI and display
        color_scheme = self._get_color_scheme()
        self.tui = TUI(
            color_scheme=color_scheme,
            refresh_rate=self.config.refresh_rate,
        )

        # Sensors
        self.sensors: Dict[str, any] = {}
        self._initialize_sensors()

        # Data history manager
        self.data_history = DataHistoryManager(buffer_capacity=self.config.buffer_size)

        # Threshold and alarm management
        self.threshold_manager = ThresholdManager()
        self.alarm_manager = AlarmManager(self.threshold_manager)

        # Control flags
        self.running = False
        self.sensor_thread: Optional[threading.Thread] = None

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration.

        Returns:
            Logger instance.
        """
        logger = logging.getLogger("sensetop")
        logger.setLevel(logging.DEBUG)

        # Create file handler
        handler = logging.FileHandler(self.config.log_file)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def _get_color_scheme(self) -> Optional[ColorScheme]:
        """Get the color scheme based on configuration.

        Returns:
            ColorScheme instance or None for default.
        """
        schemes = ColorManager.get_available_schemes()
        theme = self.config.theme

        if theme in schemes:
            return schemes[theme]

        self.logger.warning(f"Unknown theme: {theme}, using default")
        return None

    def _initialize_sensors(self) -> None:
        """Initialize all sensors."""
        try:
            # IMU sensor
            self.sensors["imu"] = IMUSensor(use_mock=self.config.use_mock)
            self.sensors["imu"].initialize()

            # Environmental sensor
            self.sensors["environmental"] = EnvironmentalSensor(use_mock=self.config.use_mock)
            self.sensors["environmental"].initialize()

            # System sensor
            self.sensors["system"] = SystemSensor(use_mock=self.config.use_mock)
            self.sensors["system"].initialize()

            self.logger.info("All sensors initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize sensors: {e}")
            raise

    def _sensor_read_loop(self) -> None:
        """Continuously read sensor data in a background thread."""
        self.logger.info("Sensor read loop started")

        while self.running:
            try:
                # Read from all sensors
                sensor_data = {}

                for sensor_name, sensor in self.sensors.items():
                    try:
                        reading = sensor.read()
                        sensor_data[sensor_name] = reading

                        # Store readings in data history and check thresholds
                        if sensor_name == "imu":
                            self.data_history.add_reading("accel_x", reading.value.accel_x)
                            self.data_history.add_reading("accel_y", reading.value.accel_y)
                            self.data_history.add_reading("accel_z", reading.value.accel_z)
                        elif sensor_name == "environmental":
                            self.data_history.add_reading("temperature", reading.value.temperature)
                            self.data_history.add_reading("humidity", reading.value.humidity)
                            self.data_history.add_reading("pressure", reading.value.pressure)
                            # Check thresholds
                            self.alarm_manager.check_and_create_alarm("temperature", reading.value.temperature)
                            self.alarm_manager.check_and_create_alarm("humidity", reading.value.humidity)
                            self.alarm_manager.check_and_create_alarm("pressure", reading.value.pressure)
                        elif sensor_name == "system":
                            self.data_history.add_reading("cpu_temperature", reading.value.cpu_temp)
                            self.data_history.add_reading(
                                "memory_percent", reading.value.memory_percent
                            )
                            # Check thresholds
                            self.alarm_manager.check_and_create_alarm("cpu_temperature", reading.value.cpu_temp)
                            self.alarm_manager.check_and_create_alarm("memory_percent", reading.value.memory_percent)

                    except Exception as e:
                        self.logger.error(f"Error reading {sensor_name}: {e}")

                # Sleep until next read
                time.sleep(self.config.sensor_interval / 1000.0)

            except Exception as e:
                self.logger.error(f"Error in sensor read loop: {e}")
                time.sleep(1)  # Prevent busy loop on error

        self.logger.info("Sensor read loop stopped")

    def _setup_ui(self) -> None:
        """Set up the user interface views."""
        # Create dashboard view
        dashboard = DashboardView(
            name="dashboard",
            color_manager=self.tui.color_manager,
            app=self,
        )
        self.tui.register_view(dashboard)

        # Create graph view
        graph_view = GraphView(
            name="graphs",
            color_manager=self.tui.color_manager,
            app=self,
        )
        self.tui.register_view(graph_view)

        # Create alert view
        alert_view = AlertView(
            name="alerts",
            color_manager=self.tui.color_manager,
            app=self,
        )
        self.tui.register_view(alert_view)

        # Create settings view
        settings_view = SettingsView(
            name="settings",
            color_manager=self.tui.color_manager,
            app=self,
        )
        self.tui.register_view(settings_view)

        # Create help view
        help_view = HelpView(
            name="help",
            color_manager=self.tui.color_manager,
        )
        self.tui.register_view(help_view)

        # Set dashboard as the starting view
        self.tui.set_current_view("dashboard")

    def run(self) -> None:
        """Run the application.

        This is the main entry point that starts the UI event loop.
        """
        self.running = True
        self.logger.info("Starting SenseTop application")

        # Start sensor read thread
        self.sensor_thread = threading.Thread(
            target=self._sensor_read_loop,
            daemon=True,
        )
        self.sensor_thread.start()

        try:
            # Run the curses application
            curses.wrapper(self._run_curses)
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except curses.error as e:
            self.logger.error(f"Curses error: {e}")
            # Curses errors during wrapper initialization/cleanup should not be re-raised
            # as they indicate terminal state issues, not application logic errors
        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
            raise
        finally:
            self.shutdown()

    def _run_curses(self, stdscr: "curses._CursesWindow") -> None:
        """Run the application within curses context.

        Args:
            stdscr: The curses window object.
        """
        try:
            # Initialize TUI
            self.tui.initialize(stdscr)
            self._setup_ui()

            # Main event loop
            while self.running:
                # Draw current view
                self.tui.draw()

                # Handle input
                key = stdscr.getch()
                if not self.tui.handle_input(key):
                    self.running = False

        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            self.running = False

    def shutdown(self) -> None:
        """Shutdown the application and clean up resources."""
        self.logger.info("Shutting down SenseTop application")

        # Stop running
        self.running = False

        # Wait for sensor thread
        if self.sensor_thread is not None:
            self.sensor_thread.join(timeout=2.0)

        # Shutdown TUI
        self.tui.shutdown()

        # Shutdown sensors
        for sensor in self.sensors.values():
            try:
                sensor.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down sensor: {e}")

        self.logger.info("Application shutdown complete")
