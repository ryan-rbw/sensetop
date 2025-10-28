#!/usr/bin/env python3
"""
Quick demo script to run SenseTop locally with mocked sensors.

This allows you to test the full application on your laptop without
needing a Raspberry Pi or Sense HAT hardware.

Usage:
    python run_local_demo.py

The script will:
- Use mock data for all sensors
- Display the interactive dashboard
- Allow you to navigate between views
- Show alarm system in action
- Test threshold management

Keyboard Controls:
    1 - Dashboard view
    2 - Graphs view
    3 - Alerts view
    4 - Settings view
    h - Help
    q - Quit
    a - Acknowledge all alarms (in alerts view)
    r - Reset to defaults (in settings view)
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sensetop.app import SenseTopApp
from sensetop.config import Config


def main() -> int:
    """Run the SenseTop app with mocked sensors."""
    print("=" * 70)
    print("SenseTop Local Demo - Using Mocked Sensors")
    print("=" * 70)
    print()
    print("Configuration:")
    print("  - Sensors: MOCKED (no hardware required)")
    print("  - Theme: dark")
    print("  - Refresh Rate: 500ms")
    print()
    print("Keyboard Controls:")
    print("  1/2/3/4 - Switch between Dashboard/Graphs/Alerts/Settings")
    print("  h       - Help screen")
    print("  q       - Quit application")
    print()
    print("Starting application...")
    print()

    app: SenseTopApp | None = None
    try:
        # Create config with mock sensors enabled
        config = Config(
            use_mock=True,  # Use mocked sensor data
            theme="dark",
            refresh_rate=500,
            sensor_interval=500,
            enable_logging=True,
        )

        # Create and run the application
        app = SenseTopApp(config=config)
        app.run()
        return 0

    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        return 130

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Ensure proper cleanup
        if app is not None:
            try:
                app.shutdown()
            except Exception as e:
                print(f"Error during shutdown: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
