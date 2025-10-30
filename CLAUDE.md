# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SenseTop** is a real-time terminal-based monitoring application for the Sense HAT module on Raspberry Pi 5. It displays sensor data (temperature, humidity, pressure, IMU), system metrics, and historical trends in an interactive curses-based TUI, similar to HTOP/JTOP but for Sense HAT sensors.

**Current Version:** 0.2.0-dev (preparing for first release)
**Target Platform:** Raspberry Pi 5 with Sense HAT (supports mock mode for development)
**Test Coverage:** 62.79% (190 passing tests, exceeds 60% target)

## ⚠️ IMPORTANT: Multi-Environment Project

**BEFORE starting any work, you MUST determine which environment you're in.** This project is developed across multiple environments with different capabilities.

### Environment Detection

**Quick method (recommended):**
```bash
./scripts/detect_environment.sh
```

This script automatically detects your environment and provides guidance.

**Manual detection:**
```bash
# Check if on Raspberry Pi
cat /proc/device-tree/model 2>/dev/null || echo "Not a Raspberry Pi"

# Check for Sense HAT hardware
i2cdetect -y 1 2>/dev/null | grep -E "(1c|5f|6a)" && echo "✓ Sense HAT detected" || echo "✗ No Sense HAT hardware"

# Check Python version
python3 --version

# Check OS
uname -a
```

### Environment Types

**1. Development Environment (Ubuntu Desktop/Laptop)**
- **Purpose:** Code development, testing with mocks, git operations
- **Characteristics:**
  - Ubuntu (or other Linux/macOS)
  - No Sense HAT hardware
  - `/proc/device-tree/model` does not exist or not a Pi
- **Mode:** Always use `use_mock=True` or run via `make demo`
- **Capabilities:** Full development workflow (code, test, lint, format, commit, push)

**2. Target Hardware Environment (Raspberry Pi 5)**
- **Purpose:** Hardware validation, real sensor testing, final verification
- **Characteristics:**
  - Raspberry Pi 5 Model B
  - Sense HAT connected (I2C devices at 0x1c, 0x5f, 0x6a)
  - `/proc/device-tree/model` shows "Raspberry Pi 5"
- **Mode:** Can use `use_mock=False` for real hardware testing
- **Capabilities:** Hardware validation, end-to-end testing, release verification

**3. Contributor Environment (Unknown)**
- **Purpose:** Community contributions, testing, development
- **Characteristics:** Could be any platform (Linux, macOS, Windows/WSL)
- **Mode:** Should use mocks unless they have Sense HAT hardware
- **Capabilities:** Standard development workflow with mocks

### Environment-Specific Behavior

**When on development machine:**
- Use mocked sensors by default
- Run tests with mocks: `make test`
- Use `make demo` for local testing
- Perform git operations (commit, push, PR)
- Run linting, formatting, type checking

**When on Raspberry Pi 5:**
- Can test with real hardware: `python -m sensetop`
- Can validate individual sensors with `use_mock=False`
- Run full integration tests with actual sensor data
- Verify hardware compatibility before releases
- **Warning:** Don't do heavy development here - use dev machine for coding

**When environment is unknown:**
- Default to mock mode for safety
- Run environment detection commands first
- Follow development machine workflow unless hardware confirmed

### Required Tools by Environment

After detecting your environment, ensure the necessary tools are installed.

#### All Environments - Core Tools
```bash
# Check what you have
python3 --version  # Need 3.8+
git --version
pip --version

# Install core tools (if missing)
# On Raspberry Pi OS:
sudo apt install -y python3-full python3-pip git i2c-tools

# On Ubuntu/Debian:
sudo apt install -y python3 python3-pip git
```

#### Development Environment - Testing & Quality Tools

**Option 1: Using apt (if available)**
```bash
sudo apt install -y python3-pytest python3-pytest-cov python3-pytest-asyncio
```

**Option 2: Using pipx (recommended for Raspberry Pi OS)**

pipx installs Python CLI tools in isolated environments while making them globally available. This prevents dependency conflicts and is safer than `--break-system-packages`.

```bash
# Install pipx
sudo apt install -y pipx
pipx ensurepath
# Log out and back in, or run: source ~/.bashrc

# Install development tools
pipx install pytest
pipx install black
pipx install isort
pipx install pylint
pipx install flake8
pipx install mypy

# Verify installations
pytest --version
black --version
pylint --version
flake8 --version
mypy --version
```

**What is pipx?**
- Like `apt` for Python CLI tools
- Installs each tool in its own virtual environment
- Makes commands available globally
- Prevents dependency conflicts between tools
- Safer than `pip install --break-system-packages`

Example: `pipx install black` creates an isolated venv for black but adds `black` command to your PATH.

#### Target Hardware - Sense HAT Libraries

```bash
# Ensure Sense HAT library is installed
sudo apt install -y sense-hat

# Verify I2C access
sudo apt install -y i2c-tools
i2cdetect -y 1  # Should show devices at 0x1c, 0x5f, 0x6a

# Check user permissions
groups | grep i2c || sudo usermod -a -G i2c $USER
```

#### Quick Tool Check

Run this to see what's missing:
```bash
# Check Python tools
for tool in python3 pytest black pylint flake8 isort mypy; do
    command -v $tool >/dev/null 2>&1 && echo "✓ $tool" || echo "✗ $tool (missing)"
done

# Check system tools
for tool in git gh i2cdetect; do
    command -v $tool >/dev/null 2>&1 && echo "✓ $tool" || echo "✗ $tool (missing)"
done
```

## Essential Commands

### Development Workflow
```bash
# Install development dependencies
make install-dev

# Run tests with coverage (requires 60%+ coverage to pass)
make test

# Run specific test file
pytest tests/test_sensors.py -v

# Run single test
pytest tests/test_sensors.py::TestIMUSensor::test_read_success -v

# Run linting (pylint, flake8)
make lint

# Format code (black, isort with 100-char line length)
make format

# Type checking
make type-check

# Build distribution package
make build

# Clean build artifacts
make clean
```

### Running the Application

**Check environment first, then run appropriately:**

```bash
# On development machine (no hardware) - ALWAYS use mocks
python run_local_demo.py
# or
make demo

# On Raspberry Pi 5 with Sense HAT - use real hardware
python -m sensetop
# or
make run

# Test individual sensors with real hardware (Pi only)
python3 -c "from sensetop.sensors.environmental import EnvironmentalSensor; s = EnvironmentalSensor(use_mock=False); s.initialize(); r = s.read(); print(f'Temp: {r.value.temperature:.1f}°C'); s.shutdown()"
```

### Testing Strategy
- All tests use mocked Sense HAT hardware (tests/mocks/mock_sense_hat.py)
- Sensors automatically use mock mode unless explicitly configured with `use_mock=False`
- Coverage target: 60%+ (enforced in pytest config)
- Test execution time: ~2-3 seconds for full suite

### Release Management
```bash
# Bump version (major/minor/patch)
python scripts/bump_version.py patch  # Updates setup.py and creates git tag

# Tag triggers GitHub Actions release workflow automatically
git push origin v0.2.0  # Publishes to TestPyPI, runs multi-version tests
```

## Architecture Overview

### Core Design Pattern: Sensor → Data → Display Pipeline

The application follows a three-layer architecture with threading for concurrent sensor reads:

1. **Sensor Layer** (`sensetop/sensors/`)
   - Abstract base class: `Sensor` defines contract for all sensor implementations
   - All sensors inherit from `Sensor` and implement: `initialize()`, `read()`, `shutdown()`, `get_specification()`
   - Returns `SensorReading` dataclass with timestamp, value, status, unit, metadata
   - Tracks success/error rates and automatically updates `SensorStatus` (OK/WARNING/ERROR)
   - Three sensor types:
     - `IMUSensor`: LSM9DS1 9-DOF IMU (accelerometer, gyroscope, magnetometer, orientation)
     - `EnvironmentalSensor`: HTS221/LPS25H (temperature, humidity, pressure, derived metrics)
     - `SystemSensor`: Raspberry Pi metrics (CPU temp, memory, uptime)

2. **Data Layer** (`sensetop/data/`)
   - `CircularBuffer`: Generic time-series buffer with O(1) operations for historical data
   - `DataHistoryManager`: Multi-sensor tracking, maintains separate buffers per sensor, calculates statistics (min/max/avg), detects trends
   - `ThresholdManager`: JSON-persisted threshold configurations with warning/critical zones
   - `AlarmManager`: Tracks alarm events (max 500), severity levels, acknowledgment state
   - `CSVExporter`: Exports sensor data and statistics to CSV files

3. **Display Layer** (`sensetop/display/`)
   - `TUI`: Main framework managing curses window, view routing, keyboard input
   - Five views (each inherits from base view concept):
     - `DashboardView`: Real-time sensor values with color-coded status
     - `GraphView`: Historical trends with Unicode sparklines and ASCII graphs
     - `AlertView`: Active alarms with severity indicators and acknowledgment
     - `SettingsView`: Threshold configuration (currently read-only)
     - `HelpView`: Keyboard shortcuts and documentation
   - `ColorManager`: Three themes (dark, light, colorful) with status-based coloring
   - `GraphRenderer`: Visualization engine for sparklines, bar charts, line graphs

### Application Lifecycle

The `SenseTopApp` class orchestrates everything:
1. Initializes sensors, data managers, threshold/alarm systems
2. Spawns background thread (`_sensor_read_loop`) for polling sensors at configured interval
3. Main thread runs TUI event loop for rendering and keyboard input
4. Sensor thread reads all sensors, updates data history, checks thresholds, triggers alarms
5. TUI renders current view at configured refresh rate
6. Clean shutdown stops sensor thread, closes TUI, releases resources

### Key Architectural Decisions

**Threading Model:** Sensor reads run in separate thread to prevent blocking UI. Data is synchronized via `DataHistoryManager` which is thread-safe for concurrent reads/writes.

**Mock Framework:** All sensors support `use_mock=True` parameter. Mock implementations generate realistic data without hardware, enabling development on any platform and automated CI testing.

**Configuration Persistence:** User config, thresholds stored as JSON in `~/.sensetop/`. Settings persist across sessions.

**Error Handling Philosophy:** Sensors track error rates and auto-adjust status. Application degrades gracefully - if one sensor fails, others continue. Failed sensor reads don't crash the app.

**Display Abstraction:** Views are independent components. TUI handles routing. Adding new views requires implementing view interface and adding to TUI view registry.

## Critical Implementation Details

### Sensor Base Class Contract
When creating or modifying sensors, the base class (`sensors/base.py`) enforces:
- Must call `_record_success()` after successful reads to increment counter
- Must call `_record_error(exception)` on failures to track error rate
- Error rate > 50% automatically changes status to ERROR (warning at <50%)
- The `error_rate` property is calculated dynamically from `_error_count` and `_reading_count`

### Threshold Checking in Sensor Loop
The sensor read loop (`app.py:_sensor_read_loop`) performs threshold checking:
1. Reads all sensors and stores in data history
2. For each reading, calls `threshold_manager.check_threshold(sensor_name, value)`
3. If violated, calls `alarm_manager.trigger_alarm(sensor_name, value, severity)`
4. UI automatically displays active alarms in AlertView

### Data History Buffer Sizing
- Default buffer capacity: 120 data points per sensor
- Circular buffer automatically overwrites oldest data
- Statistics (min/max/avg) calculated over entire buffer window
- GraphView displays up to 60 most recent points for visualization

### Color Scheme System
Colors are status-aware:
- `ColorScheme` defines palette (background, foreground, status colors)
- Status colors: green (OK), yellow (WARNING), red (ERROR/CRITICAL)
- All views use `ColorManager.get_status_color()` for consistent status display
- Theme changes applied immediately without restart

## Code Quality Standards

### Style Enforcement
- **Black formatting**: 100-char line length (configured in pyproject.toml)
- **PEP 8 compliance**: Enforced via pylint/flake8
- **Import sorting**: isort with black profile
- **Type hints**: Required for all public functions (mypy checking enabled)
- **Docstrings**: Google-style docstrings for all public classes/functions

### Testing Requirements
- 60%+ coverage required (pytest fails below threshold)
- All new features must include unit tests
- Sensor tests must use mock framework (don't require hardware)
- Integration tests in `test_app.py` verify end-to-end functionality
- Performance tests should validate <100ms update latency

### Pre-commit Checklist
Before committing code changes:
1. `make format` - Format with black/isort
2. `make lint` - Check with pylint/flake8 (must pass cleanly)
3. `make type-check` - Validate type hints with mypy
4. `make test` - Run full test suite (must reach 60%+ coverage)
5. Verify in demo mode: `make demo` (manually test changes in TUI)

## Common Development Patterns

### Adding a New Sensor
1. Create new class in `sensetop/sensors/` inheriting from `Sensor`
2. Implement required methods: `initialize()`, `read()`, `shutdown()`, `get_specification()`
3. Call `_record_success()` or `_record_error()` in `read()` method
4. Add mock implementation for testing (support `use_mock` parameter)
5. Register in `app.py:_initialize_sensors()`
6. Add default thresholds in `data/thresholds.py:DEFAULT_THRESHOLDS`
7. Write unit tests in `tests/test_sensors.py`

### Adding a New View
1. Create view class in `display/views.py` (or separate file)
2. Implement `render(self, stdscr, data)` method using curses
3. Handle keyboard input in view or delegate to TUI
4. Register in `TUI.views` dictionary with key binding
5. Add keyboard shortcut to `HelpView` documentation
6. Write UI tests in `tests/test_display.py`

### Modifying Thresholds
1. Update `DEFAULT_THRESHOLDS` in `data/thresholds.py` for new defaults
2. Thresholds are JSON-persisted per user in `~/.sensetop/thresholds.json`
3. Users can reset to defaults via SettingsView (press 'r')
4. Threshold validation happens in `SensorThreshold.validate()`
5. Check implementation in `SensorThreshold.check_value()` returns (status, violated)

### Data Export
CSV export implemented in `data/export.py`:
- `export_sensor_data()`: Export single sensor time-series
- `export_all_sensors()`: Export all sensors with timestamps
- `export_summary()`: Export statistical summary (min/max/avg)
- Files saved to `~/.sensetop/exports/` with timestamp in filename

## Configuration Files

User configuration stored in `~/.sensetop/`:
- **config.json**: Refresh rate, theme, buffer size, temperature units, enabled sensors
- **thresholds.json**: Per-sensor threshold configurations
- **sensetop.log**: Application debug logs
- **exports/**: CSV export directory

## Dependencies and Platform Notes

### Core Dependencies
- `sense-hat>=2.2.0`: Official Sense HAT library (only on Pi with hardware)
- `smbus2>=0.4.1`: I2C communication (mock when not on Pi)
- `numpy>=1.19.0`: Data processing and statistics
- `pytz>=2021.1`: Timestamp timezone handling
- `curses`: Built-in Python TUI library (not available on Windows - use WSL)

### Python Version Support
- Minimum: Python 3.8
- Tested: 3.8, 3.9, 3.10, 3.11 (via GitHub Actions)
- Type hints use 3.8+ syntax (no future imports needed)

### Platform Compatibility
- **Raspberry Pi 5**: Primary target, runs with real Sense HAT hardware
- **Linux/macOS**: Runs in mock mode for development (curses supported)
- **Windows**: Not directly supported (use WSL for curses compatibility)

## CI/CD Pipeline

GitHub Actions workflows (`.github/workflows/`):
- **tests.yml**: Multi-version testing (3.8-3.11), requires 60%+ coverage
- **lint.yml**: Code quality checks (pylint, flake8, black, isort, mypy)
- **build.yml**: Package building, installation verification
- **release.yml**: Triggered by git tags, publishes to TestPyPI, creates GitHub Release

All workflows run on push/PR to master branch.

## Known Limitations and Future Work

### Current Limitations
- **SettingsView is read-only**: Can view thresholds but not edit in-app (must edit JSON manually)
- **Display test coverage**: Views at 30% coverage (curses mocking complex, not blocking)
- **No persistent alarm logging**: Alarms stored in memory only (max 500 events)
- **No threshold hysteresis**: Can cause alarm flapping on boundary values
- **Python 3.13 compatibility**: Running on Python 3.13.5 (newer than CI-tested 3.8-3.11, but appears compatible)

### Planned Enhancements (v0.3.0+)
- In-app threshold editing in SettingsView
- Persistent alarm history to file
- Hysteresis/debouncing for threshold violations
- LED matrix visualization on Sense HAT
- Data export scheduling (automatic CSV exports)
- Web interface for remote monitoring

## Documentation Resources

- **SPEC.md**: Complete project specification, requirements, architecture
- **JOURNAL.md**: Development history, session notes, decisions (77k+ lines)
- **RUNNING_LOCALLY.md**: Guide for running in mock mode without hardware
- **README.md**: Quick start, installation, basic usage

## Release Process

Current state: **Ready for v0.2.0 release to TestPyPI - Hardware validated ✓**

Hardware validation completed on Raspberry Pi 5:
- ✓ I2C devices detected at expected addresses (0x1c, 0x5f, 0x6a, etc.)
- ✓ Environmental sensor reading real data (temp, humidity, pressure)
- ✓ IMU sensor operational (pitch, roll, yaw)
- ✓ System sensor functional (CPU temp, memory)
- ✓ User has I2C permissions

### Release Workflow (Multi-Environment)

**On development machine (Ubuntu):**
1. Verify all tests pass with mocks: `make test`
2. Run linting and formatting: `make lint && make format`
3. Commit changes and push to GitHub
4. Create release tag: `git tag v0.2.0 && git push origin v0.2.0`
5. Monitor GitHub Actions for CI/CD pipeline

**On Raspberry Pi 5 (before or after release):**
1. Pull latest code: `git pull origin master`
2. Run tests on hardware: `make test` (validates with mocks)
3. Run full application with real sensors: `python -m sensetop`
4. Validate all TUI features work with hardware
5. Test installation from TestPyPI

**GitHub Actions (automatic):**
1. Runs multi-version tests (3.8-3.11)
2. Publishes to TestPyPI
3. Creates GitHub Release
4. Runs post-release validation

Next steps for v0.2.0:
1. [Dev machine] Push v0.2.0 tag: `git push origin v0.2.0`
2. [GitHub] Monitor Actions workflow completion
3. [Pi] Validate installation: `pip install -i https://test.pypi.org/simple/ sensetop`
4. [Pi] Run end-to-end validation with hardware
5. Gather user feedback before production PyPI release

## Development Philosophy

This project follows **specification-driven development**:
- SPEC.md is the source of truth for requirements
- All features implemented per specification sections
- Quality-first approach: comprehensive testing, documentation, CI/CD
- Professional standards: production-ready code, enterprise-grade testing
- User-centered design: responsive UI, clear feedback, comprehensive help

When modifying code, reference the relevant specification section and update SPEC.md if requirements change.

## Git Workflow for Multi-Environment Development

### Typical Workflow

**Development Phase (Ubuntu/Dev Machine):**
1. Create feature branch: `git checkout -b feature/name`
2. Write code with mock sensors
3. Write/update tests: `make test`
4. Lint and format: `make lint && make format`
5. Commit changes: `git commit -m "Add feature"`
6. Push to GitHub: `git push origin feature/name`
7. Create pull request

**Validation Phase (Raspberry Pi 5):**
1. Pull latest code: `git pull origin master` or `git checkout feature/name`
2. Test with real hardware: `python -m sensetop`
3. Validate sensor readings, UI behavior, performance
4. Report issues back to dev machine for fixes

**Release Phase:**
1. [Dev] Merge PR to master
2. [Dev] Create and push tag: `git tag v0.x.x && git push origin v0.x.x`
3. [GitHub] CI/CD pipeline builds and publishes
4. [Pi] Test installation from TestPyPI
5. [Pi] Final validation with hardware

### Important Notes for Contributors

- **Never commit directly on Raspberry Pi** - use dev machine for git operations
- **Always use mocks in tests** - tests must pass on any environment without hardware
- **Hardware validation is separate from CI/CD** - CI runs on GitHub runners (no hardware)
- **Document environment requirements** - if adding features that need specific env, note it
