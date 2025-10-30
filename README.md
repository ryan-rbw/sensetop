# SenseTop

[![Tests](https://github.com/ryan-rbw/sensetop/actions/workflows/tests.yml/badge.svg)](https://github.com/ryan-rbw/sensetop/actions/workflows/tests.yml)
[![Lint](https://github.com/ryan-rbw/sensetop/actions/workflows/lint.yml/badge.svg)](https://github.com/ryan-rbw/sensetop/actions/workflows/lint.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time terminal-based monitoring application for the Sense HAT module on Raspberry Pi 5. Think **HTOP for Sense HAT** - it displays sensor data, environmental metrics, and system information in an interactive curses-based TUI with live updates, historical graphs, and threshold alarms.

```
┌─────────────────────── SenseTop Dashboard ───────────────────────┐
│  Temperature: 47.3°C ↑    Humidity: 18.4% →    Pressure: 1005 hPa │
│  Pitch: 1.9°  Roll: 0.5°  Yaw: 0.0°                              │
│  CPU: 52.3°C  Memory: 45.2%  Uptime: 2d 4h 15m                   │
│                                                                    │
│  [1] Dashboard  [2] Graphs  [3] Alerts  [4] Settings  [h] Help   │
└────────────────────────────────────────────────────────────────────┘
```

## ✨ Features

### 🎯 Real-Time Monitoring
- **Environmental Sensors**: Temperature, humidity, atmospheric pressure
- **9-DOF IMU**: Accelerometer, gyroscope, magnetometer, orientation (pitch/roll/yaw)
- **System Metrics**: CPU temperature, memory usage, uptime
- **Live Updates**: Configurable refresh rates (100ms - 5s)

### 📊 Interactive TUI
- **Dashboard View**: Real-time sensor values with color-coded status indicators
- **Graph View**: Historical trends with Unicode sparklines and ASCII charts
- **Alert View**: Active alarms with severity indicators (🔴 Critical, 🟡 Warning)
- **Settings View**: Threshold configuration and system settings
- **Help View**: Comprehensive keyboard shortcuts and documentation

### 💡 LED Matrix Display
- **Text Scrolling**: Display custom text with horizontal scrolling animation
- **Worm Animation**: 6-segment animated worm following clockwise spiral path
- **Interactive Control**: Press **L** to cycle through modes (OFF → TEXT → WORM)
- **Text Input Dialog**: Enter custom messages up to 100 characters
- **Configuration Persistence**: Remembers your last mode and settings
- **Terminal Preview**: ASCII representation for remote development over SSH

### 🎨 Customization
- **Three Color Themes**: Dark, Light, Colorful
- **Threshold Management**: Configurable warning/critical ranges per sensor
- **Data Export**: CSV export for sensor readings and statistics
- **Persistent Config**: JSON-based configuration in `~/.sensetop/`

### 🧪 Development-Friendly
- **Mock Mode**: Full functionality without hardware for development/testing
- **Multi-Environment**: Develop on Ubuntu/macOS, validate on Raspberry Pi
- **222 Tests**: 63.64% code coverage, comprehensive test suite
- **CI/CD**: GitHub Actions for testing, linting, building, releases

## 🚀 Quick Start

### Environment Detection

**Important**: SenseTop supports multi-environment development. Run this first to detect your environment:

```bash
./scripts/detect_environment.sh
```

This determines if you're on a **Development Machine** (Ubuntu/laptop) or **Target Hardware** (Raspberry Pi 5 with Sense HAT).

### Installation

#### On Raspberry Pi 5 with Sense HAT (Target Hardware)

```bash
# Clone the repository
git clone https://github.com/ryan-rbw/sensetop.git
cd sensetop

# Ensure I2C is enabled (if not already)
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable

# Run with real sensors
python3 -m sensetop
```

#### On Development Machine (Ubuntu/macOS/Linux)

```bash
# Clone the repository
git clone https://github.com/ryan-rbw/sensetop.git
cd sensetop

# Install dependencies
pip install -r requirements.txt

# Run with mocked sensors (no hardware required)
python3 run_local_demo.py
```

See [RUNNING_LOCALLY.md](RUNNING_LOCALLY.md) for detailed instructions on running without hardware.

## 🎮 Usage

### Keyboard Controls

| Key | Action |
|-----|--------|
| **1** | Dashboard view (real-time sensor data) |
| **2** | Graphs view (historical trends) |
| **3** | Alerts view (active alarms) |
| **4** | Settings view (thresholds) |
| **L** | Cycle LED modes (OFF → TEXT → WORM) |
| **h** or **?** | Help screen |
| **q** or **ESC** | Quit application |
| **↑/↓** or **j/k** | Navigate lists |
| **a** | Acknowledge all alarms (in Alerts view) |
| **r** | Reset thresholds to defaults (in Settings view) |

### Views Overview

**Dashboard (1)** - Real-time monitoring
- Live sensor values with color-coded status
- Trend indicators (↑ rising, → stable, ↓ falling)
- Status badges (OK/WARNING/ERROR)

**Graphs (2)** - Historical visualization
- Unicode sparklines showing trends over time
- Statistical summaries (min/max/avg)
- Navigate between sensors with arrow keys

**Alerts (3)** - Alarm management
- Active alarms with severity and timestamps
- Acknowledge alarms individually or all at once
- History of recent violations

**Settings (4)** - Configuration
- View threshold values (warning/critical ranges)
- Navigate between sensors
- Reset to defaults (read-only editing for now)

**Help (h)** - Complete documentation
- All keyboard shortcuts
- Feature descriptions
- Version information

## 💻 Development

### Prerequisites

SenseTop requires different tools depending on your environment. After running `./scripts/detect_environment.sh`, install the necessary tools:

#### Core Dependencies (All Environments)

```bash
# On Raspberry Pi OS
sudo apt install -y python3-full python3-pip git i2c-tools

# On Ubuntu/Debian
sudo apt install -y python3 python3-pip git

# Install Python dependencies
pip install -r requirements.txt
```

#### Development Tools (Optional - for contributing)

**Testing and Quality Tools:**

```bash
# Install pytest (on systems where apt has it)
sudo apt install -y python3-pytest python3-pytest-cov python3-pytest-asyncio

# Install linting tools via pipx (recommended for Raspberry Pi OS)
sudo apt install -y pipx
pipx ensurepath

# Install formatters and linters
pipx install black
pipx install isort
pipx install pylint
pipx install flake8
pipx install mypy

# Verify installations
pytest --version
black --version
pylint --version
```

**What is pipx?**

`pipx` is like `apt` for Python CLI tools - it installs them in isolated environments while making them available globally. This is safer than `pip install --break-system-packages` and prevents dependency conflicts.

### Common Development Tasks

```bash
# Run tests with coverage
make test

# Format code (black, isort)
make format

# Lint code (pylint, flake8)
make lint

# Type checking
make type-check

# Build package
make build

# Run with mocks (dev machine)
make demo

# Run with real hardware (Raspberry Pi)
make run

# Clean build artifacts
make clean
```

### Testing

```bash
# Run full test suite
make test

# Run specific test file
pytest tests/test_sensors.py -v

# Run single test
pytest tests/test_sensors.py::TestIMUSensor::test_read_success -v

# Run tests with verbose output
pytest -vv
```

All tests use mocked Sense HAT hardware, so they run on any platform without requiring physical sensors.

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive guide for Claude Code (architecture, commands, patterns)
- **[SPEC.md](SPEC.md)** - Complete project specification and requirements
- **[RUNNING_LOCALLY.md](RUNNING_LOCALLY.md)** - Detailed guide for running without hardware
- **[JOURNAL.md](JOURNAL.md)** - Development history and session notes (77k+ lines)

## 🏗️ Architecture

SenseTop follows a three-layer architecture:

```
┌─────────────────────────────────────────┐
│         Display Layer (TUI)             │
│  Dashboard │ Graphs │ Alerts │ Settings │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Data Layer                     │
│  History │ Buffers │ Thresholds │ Alarms│
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Sensor Layer                    │
│    IMU │ Environmental │ System          │
└──────────────────────────────────────────┘
```

- **Sensor Layer**: Abstract base class with IMU, Environmental, System implementations
- **Data Layer**: Circular buffers, history management, threshold checking, alarm tracking
- **Display Layer**: Curses-based TUI with multiple views and color schemes

Sensors run in a background thread for non-blocking UI updates. All components support mock mode for development without hardware.

## 🔄 Multi-Environment Workflow

### Development Machine (Ubuntu/Laptop)
- **Purpose**: Code development, testing, commits, PRs
- **Mode**: Always use mocks (`make demo`)
- **Workflow**: Write code → Test → Lint → Format → Commit → Push

### Target Hardware (Raspberry Pi 5)
- **Purpose**: Hardware validation, real sensor testing
- **Mode**: Can use real hardware (`python -m sensetop`)
- **Workflow**: Pull code → Validate → Test → Report issues

See [CLAUDE.md](CLAUDE.md) for detailed multi-environment development guidelines.

## 🚢 Release Status

**Current Version**: 0.2.0-dev (preparing for first release)

**Status**: ✓ Hardware Validated
- ✓ All sensors tested on Raspberry Pi 5
- ✓ 190 tests passing (62.79% coverage)
- ✓ CI/CD pipeline configured
- ✓ Ready for TestPyPI release

**Release Timeline**:
- **v0.2.0** (Current): First public release, core functionality complete
- **v0.3.0** (Planned): In-app threshold editing, persistent alarm history, hysteresis

## 🛠️ Troubleshooting

### "No module named 'sense_hat'"
On Raspberry Pi, install the Sense HAT library:
```bash
sudo apt install -y sense-hat
```

### "Permission denied" when accessing I2C
Add your user to the i2c group:
```bash
sudo usermod -a -G i2c $USER
# Log out and back in for changes to take effect
```

### "Terminal too small" error
Resize your terminal to at least 80 columns × 24 rows.

### Tests fail with coverage errors
Ensure pytest-cov is installed:
```bash
pip install pytest-cov
# or
sudo apt install python3-pytest-cov
```

### Mock sensors not working on dev machine
Ensure you're using the demo script:
```bash
python3 run_local_demo.py
# NOT: python -m sensetop (requires hardware)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Check environment: `./scripts/detect_environment.sh`
2. Use mocks for development (tests must pass without hardware)
3. Follow PEP 8 style guidelines
4. Add tests for new features (maintain 60%+ coverage)
5. Run `make lint && make format` before committing
6. Update documentation as needed

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

## 📊 Project Stats

- **Lines of Code**: 4,268 (production) + 2,612 (tests)
- **Test Coverage**: 62.79% (190 tests, 100% pass rate)
- **Python Versions**: 3.8, 3.9, 3.10, 3.11 (3.13 compatible)
- **Development Time**: ~10 sessions over 3 days
- **Documentation**: 90,000+ lines across SPEC, JOURNAL, guides

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [Sense HAT](https://www.raspberrypi.com/products/sense-hat/) on Raspberry Pi 5
- Inspired by [htop](https://htop.dev/) and [jtop](https://github.com/rbonghi/jetson_stats)
- Developed with specification-driven development methodology

---

**Repository**: https://github.com/ryan-rbw/sensetop
**Issues**: https://github.com/ryan-rbw/sensetop/issues
**Version**: 0.2.0-dev
**Status**: Ready for First Release 🚀
