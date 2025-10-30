# SenseTop - Sense HAT Monitoring Application Specification

## Overview

SenseTop is a real-time monitoring application for the Sense HAT module on Raspberry Pi 5, providing a terminal-based interface similar to HTOP or JTOP. It displays sensor data, environmental metrics, and system configuration in an interactive dashboard with live updates.

---

## 🎯 Project Specification

### 1. Core Functionality

#### Sensor Data Monitoring
- **Temperature Sensors**:
  - CPU temperature from on-board sensor
  - Housing temperature measurements
  - Real-time trend display with min/max values

- **Humidity Sensor**:
  - Relative humidity percentage (0-100%)
  - Historical data tracking
  - Humidity trend visualization

- **Pressure Sensor**:
  - Atmospheric pressure in hPa (hectopascals)
  - Altitude calculation (optional derived metric)
  - Pressure trend tracking

- **Motion & Orientation Sensors**:
  - 9-DOF IMU (accelerometer, gyroscope, magnetometer)
  - Orientation angles (pitch, roll, yaw)
  - G-force acceleration values
  - Motion/tap detection events

#### Display Features
- **Real-Time Dashboard**:
  - Live-updating sensor values with configurable refresh rates (100ms - 5s)
  - Color-coded indicators for normal/warning/critical ranges
  - Historical graphs for temperature and humidity (last 60 data points)
  - Status indicators for each sensor (OK/WARNING/ERROR)

- **Sensor Configuration Panel**:
  - Calibration status for each sensor
  - Current sensor operation mode
  - Data collection frequency
  - Hardware version and firmware information

- **System Information**:
  - CPU usage and memory statistics
  - Uptime tracking
  - Network information (if available)
  - GPIO status and hat identification

- **Logging & Data Export**:
  - Optional CSV export of sensor readings
  - Timestamped data collection
  - Session recording capability

#### User Interaction
- Keyboard controls for navigation and mode switching
- Interactive menu system for sensor selection and display options
- Customizable display layouts and themes
- Help system and keyboard shortcuts display

#### LED Matrix Display Control
The Sense HAT features an 8×8 RGB LED matrix that can be controlled for visual feedback and information display. SenseTop provides an interactive LED control interface accessible from the main dashboard.

- **LED Display Mode Selection**:
  - Interactive cursor-based selection menu on dashboard
  - Navigate modes with arrow keys (↑/↓)
  - Activate selected mode with Enter key
  - Return to sensor monitoring with Escape/q
  - Current mode displayed on dashboard status

- **Text Display Mode**:
  - **Text Input**:
    - User enters custom text string (max 100 characters)
    - Text input dialog with live preview
    - Support for alphanumeric characters, spaces, and basic punctuation
  - **Scrolling Behavior**:
    - Horizontal scrolling from right to left across the 8×8 matrix
    - Configurable scroll speed (slow/medium/fast)
    - Smooth character-by-character animation
    - Continuous loop until mode changed
  - **Color Options**:
    - **Solid Color**: Select from predefined palette (red, green, blue, yellow, cyan, magenta, white)
    - **Custom RGB**: Specify custom color (R, G, B values 0-255)
    - **Rainbow Mode**: Text color cycles through spectrum as it scrolls
    - **Gradient Mode**: Each character in different color from gradient
  - **Display Properties**:
    - 5×7 pixel font rendering (standard Sense HAT font)
    - Configurable brightness (0-100%)
    - Background color selection (default: black/off)

- **Worm Animation Mode**:
  - **Worm Properties**:
    - 6-segment animated "worm" pattern
    - Each segment is a single LED pixel
    - Each segment has a distinct color
  - **Animation Behavior**:
    - Starts at outer edge of 8×8 matrix
    - Follows clockwise spiral path inward
    - Path: outer perimeter → second ring → third ring → center
    - Smooth pixel-by-pixel movement
    - Disappears as it reaches center pixel
    - Restarts from outer edge continuously
  - **Color Configuration**:
    - **Rainbow Worm**: Each segment from spectrum (ROYGBV pattern)
    - **Custom Colors**: User defines 6 segment colors individually
    - **Themed Palettes**: Predefined color schemes (fire, ocean, forest, neon)
  - **Speed Control**:
    - Configurable animation speed (1-10, where 10 is fastest)
    - Default: medium speed (5)
    - Real-time speed adjustment without restart
  - **Spiral Algorithm**:
    - Clockwise traversal: top-right → right edge → bottom → left → inner spiral
    - Total path length: 64 pixels (entire matrix)
    - Head segment always visible, tail fades as approaching center

- **Additional LED Display Modes** (Future Enhancement):
  - Status Indicator Mode: Show sensor status with color codes
  - Graph Mode: Simple bar graph of sensor values
  - Alert Mode: Flash patterns for alarm conditions
  - Off Mode: All LEDs disabled to save power

- **LED Control Integration**:
  - **Dashboard Interface**:
    - LED mode selector widget in dashboard sidebar
    - Current mode and status displayed
    - Quick toggle with dedicated key (e.g., 'L' for LED control)
  - **Settings Persistence**:
    - LED mode and configuration saved to `~/.sensetop/led_config.json`
    - Restore previous mode on application restart
    - Default mode: Off (LEDs disabled)
  - **Resource Management**:
    - LED updates run in separate thread (non-blocking)
    - Configurable LED refresh rate (10-60 FPS)
    - Automatic cleanup on application exit (clear matrix)
  - **Hardware Integration**:
    - Direct communication via Sense HAT library (`sense_hat.set_pixel`, `sense_hat.set_pixels`)
    - Brightness control via `sense_hat.low_light` or gamma correction
    - Error handling for hardware communication failures

- **User Experience Enhancements**:
  - Live preview of LED output in terminal (8×8 ASCII representation)
  - Color picker with visual feedback
  - Animation speed preview
  - Save/load custom display configurations
  - Quick presets for common patterns

### 2. Technical Architecture

#### Software Stack
- **Language**: Python 3.8+
- **Display Framework**: curses library for TUI (Terminal User Interface)
- **Sensor Interface**:
  - Sense HAT Python library (`sense-hat` package)
  - Direct I2C communication via `smbus2` library
  - Direct filesystem access for CPU temperature (`/sys/class/thermal/`)
- **Data Processing**: NumPy for sensor data processing
- **Threading**: asyncio or threading for concurrent sensor reads
- **Configuration**: JSON or YAML for settings management

#### Hardware Interface
- **Communication Protocol**: I2C (SMBus2 interface)
- **Sense HAT Chip Connections**:
  - LSM9DS1: 9-DOF IMU (accelerometer, gyroscope, magnetometer)
  - HTS221: Temperature and humidity sensor
  - LPS25H: Pressure sensor
  - 8×8 RGB LED matrix for visual display and feedback

- **System Files Access**:
  - `/sys/class/thermal/thermal_zone0/temp` for CPU temperature
  - `/proc/meminfo` for memory statistics
  - `/proc/uptime` for system uptime

#### Data Collection Architecture
- **Sensor Polling**: Configurable polling intervals (default: 500ms)
- **Data Buffering**: Circular buffer for historical data (default: 120 data points)
- **Error Handling**: Graceful degradation when sensor reads fail
- **Hardware Detection**: Automatic detection of Sense HAT availability

### 3. Quality Requirements

#### Reliability
- **Error Recovery**:
  - Automatic retry logic for failed sensor reads
  - Graceful handling of intermittent I2C communication issues
  - Sensor timeout handling (5-second default)

- **Data Validation**:
  - Range checking for sensor values against hardware specifications
  - Detection and filtering of outlier readings
  - Sanity checks for derived metrics

- **System Stability**:
  - No memory leaks or unbounded growth
  - CPU usage < 5% during normal operation
  - Clean shutdown without resource leaks

#### Performance Targets
- **Update Latency**: < 100ms from sensor read to display update
- **UI Responsiveness**: < 50ms keyboard response time
- **Memory Footprint**: < 50MB RAM during normal operation
- **CPU Efficiency**: Optimized polling to minimize CPU usage

#### User Experience
- **Visual Clarity**:
  - Color-coded status indicators (green/yellow/red)
  - Clear numerical displays with appropriate decimal precision
  - Trend indicators (arrows or graphs)

- **Responsiveness**:
  - Immediate keyboard response
  - Smooth scrolling and navigation
  - No UI blocking during sensor reads

### 4. Project Deliverables

#### Core Application Code
- [ ] Main application entry point with initialization
- [ ] TUI framework with multiple display views/modes
- [ ] Sensor data collection module with I2C interface
- [ ] Data processing and historical tracking
- [ ] Configuration management system
- [ ] Event handling and keyboard input processing
- [ ] Color and theme management
- [ ] Graceful shutdown and cleanup

#### Sensor Modules
- [x] IMU (accelerometer, gyroscope, magnetometer) module
- [x] Temperature/humidity sensor module
- [x] Pressure sensor module
- [x] CPU temperature and system metrics module
- [ ] LED matrix control module

#### LED Matrix Control Module
- [ ] LED display manager with mode switching
- [ ] Text scrolling engine with font rendering
- [ ] Color management (solid, rainbow, gradient, custom RGB)
- [ ] Worm animation with spiral path algorithm
- [ ] LED configuration persistence (JSON)
- [ ] Thread-based LED updates (non-blocking)
- [ ] Terminal preview (8×8 ASCII representation)
- [ ] Input dialogs for text and color configuration

#### Display Components
- [ ] Dashboard view (primary display)
- [ ] Sensor details view
- [ ] Historical graph view
- [ ] Configuration panel view
- [ ] Help/shortcuts view
- [ ] Status bar and header

#### Testing Framework
- [ ] Unit tests for sensor data processing
- [ ] Integration tests for full display pipeline
- [ ] Mock Sense HAT module for testing without hardware
- [ ] UI testing framework for TUI components
- [ ] Performance benchmarking suite
- [ ] Hardware-in-the-loop testing capability

#### Documentation
- [ ] Complete README with installation instructions
- [ ] API documentation for sensor modules
- [ ] User guide with keyboard shortcuts
- [ ] Hardware setup and connection guide
- [ ] Configuration options reference
- [ ] Troubleshooting guide
- [ ] Contributing guidelines
- [ ] Architecture and design document

#### Build & Deployment
- [ ] Setup.py for Python package installation
- [ ] Requirements.txt with all dependencies
- [ ] Makefile for common development tasks
- [ ] Docker support (optional)
- [ ] Systemd service file for background operation
- [ ] Installation scripts for Pi OS

#### CI/CD Pipeline (GitHub Actions)
- [ ] Linting and code quality checks (pylint, flake8)
- [ ] Unit and integration test execution
- [ ] Code coverage analysis (target > 70%)
- [ ] Type checking with mypy
- [ ] Security scanning
- [ ] Documentation generation
- [ ] Multi-Python version testing (3.8, 3.9, 3.10, 3.11)
- [ ] Hardware compatibility validation
- [ ] ARM architecture testing (for Raspberry Pi compatibility)
- [ ] Automated build verification on target architecture

#### GitHub Project Management
- [ ] GitHub Projects board for task tracking
- [ ] Issue templates for bugs and features
- [ ] Milestone planning for development phases
- [ ] Automated workflow triggers for CI/CD
- [ ] Release automation and versioning

#### On-Target Build & Execution
- [ ] Build scripts compatible with Raspberry Pi OS environment
- [ ] Dependency installation automation for ARM/ARMv7 architecture
- [ ] Post-clone initialization script
- [ ] Local build verification on Raspberry Pi hardware
- [ ] Runtime execution scripts with graceful error handling
- [ ] Development setup guide for Pi OS (Bullseye/Bookworm)

### 5. Development Phases

#### Phase 1: Core Sensor Interface (Week 1)
- Establish I2C communication with Sense HAT
- Implement sensor data collection for all modules
- Create basic data validation and error handling
- Build mock sensor interface for testing

#### Phase 2: Terminal UI Framework (Week 2)
- Design and implement TUI structure using curses
- Create dashboard view with sensor displays
- Implement keyboard input handling
- Add color scheme and theme support
- Create help system and navigation

#### Phase 3: Data Processing & Visualization (Week 3)
- Implement circular buffer for historical data
- Create trend calculation and analysis
- Build graph visualization components
- Implement data export functionality
- Add alarm/threshold system

#### Phase 4: Testing & Quality Assurance (Week 4)
- Develop comprehensive test suite
- Achieve 70%+ code coverage
- Performance optimization and profiling
- Integration testing on Pi hardware
- Documentation completion

#### Phase 5: CI/CD & Deployment (Week 5)
- GitHub Actions pipeline setup
- Automated testing and validation
- Release automation
- Package distribution
- Production deployment scripts

#### Phase 6: LED Matrix Display Features (Week 6+)
- Implement LED display manager and mode system
- Create text scrolling engine with color support
- Develop worm animation with spiral algorithm
- Build dashboard LED control interface
- Add LED configuration persistence
- Implement thread-based LED updates
- Create terminal-based LED preview (8×8 ASCII)
- Add input dialogs for text and colors
- Test all LED modes on hardware
- Document LED feature usage

### 6. Configuration & Customization

#### User Settings
- Refresh rate (100ms - 5s)
- Display theme (light/dark/colorful)
- Temperature unit (Celsius/Fahrenheit)
- Pressure unit (hPa/mmHg/inHg)
- Enabled sensors (checkbox selection)
- Graph history length (data points)
- Alarm thresholds for each sensor

#### System Configuration
- I2C bus number (default: 1 for Raspberry Pi)
- Sensor polling interval
- Data buffer size
- Log file location
- Database file location (if applicable)

### 7. Success Criteria

#### Code Quality
- **2,000+ lines of well-structured Python code**
- **Zero critical bugs in sensor data collection**
- **Professional Python coding standards** (PEP 8 compliance)
- **Comprehensive error handling and logging**

#### Testing Quality
- **70%+ code coverage** with unit and integration tests
- **Mock framework** for testing without hardware
- **Performance benchmarks** validating latency targets
- **Automated test suite** with CI integration

#### User Experience
- **Responsive, lag-free terminal interface**
- **Intuitive keyboard navigation**
- **Clear, color-coded status information**
- **Comprehensive documentation**

#### Deployment
- **Easy installation on Raspberry Pi OS**
- **Automated CI/CD pipeline**
- **Cross-platform Python compatibility**
- **Clean package structure**

### 8. Hardware Requirements

#### Minimum
- Raspberry Pi 5 with 4GB RAM
- Sense HAT module properly installed
- Python 3.8+
- I2C enabled on Raspberry Pi

#### Recommended
- Raspberry Pi 5 with 8GB RAM
- Active cooling for Pi
- Terminal with 256-color support (for best visuals)
- 3.5+ screen width (for dashboard display)

### 9. Dependencies

#### Core Libraries
- `sense-hat`: Official Sense HAT library
- `smbus2`: SMBus interface for I2C communication
- `numpy`: Numerical data processing
- `pytz`: Timezone handling for timestamps

#### Optional Libraries
- `matplotlib` or `plotext`: For graph visualization
- `pyyaml`: Configuration file parsing
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `mypy`: Static type checking

---

## 📋 Development Guidelines

### 1. Code Organization
```
sensetop/
├── sensetop/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── app.py               # Main application class
│   ├── sensors/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract sensor class
│   │   ├── imu.py           # IMU sensor module
│   │   ├── environmental.py # Temp/humidity/pressure
│   │   ├── system.py        # CPU temp and metrics
│   │   └── mock.py          # Mock sensor for testing
│   ├── display/
│   │   ├── __init__.py
│   │   ├── tui.py           # TUI framework
│   │   ├── views.py         # Display views
│   │   ├── colors.py        # Color schemes
│   │   └── components.py    # UI components
│   ├── data/
│   │   ├── __init__.py
│   │   ├── buffer.py        # Circular buffer
│   │   ├── processor.py     # Data processing
│   │   └── export.py        # Data export
│   ├── config.py            # Configuration management
│   ├── logger.py            # Logging setup
│   └── utils.py             # Utility functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── test_sensors.py
│   ├── test_display.py
│   ├── test_data.py
│   ├── test_app.py
│   └── mocks/
│       ├── __init__.py
│       └── mock_sense_hat.py # Mock Sense HAT
├── docs/
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── TROUBLESHOOTING.md
├── .github/workflows/
│   ├── tests.yml
│   ├── lint.yml
│   └── release.yml
├── setup.py
├── setup.cfg
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── MANIFEST.in
└── LICENSE
```

### 2. Coding Standards
- **Python Style**: PEP 8 compliant, enforced with flake8/pylint
- **Type Hints**: Use type annotations for all functions
- **Documentation**: Docstrings for all public functions (Google style)
- **Error Handling**: Explicit exception handling with specific error types
- **Logging**: Comprehensive logging at appropriate levels

### 3. Testing Strategy
- **Unit Tests**: Test individual sensor modules and data processing
- **Integration Tests**: Test full data pipeline from sensor to display
- **Mock Framework**: Complete mock Sense HAT for CI/CD testing
- **UI Testing**: Automated testing of keyboard input and display output
- **Performance Tests**: Validate latency and memory targets

### 4. Version Control
- Clear commit messages following conventional commits
- Feature branches for development
- Pull requests with test validation
- Semantic versioning (MAJOR.MINOR.PATCH)

---

## 🎓 Key Principles

### Specification-Driven Development
- Front-load all requirements in this document
- Use this spec as the source of truth for development
- Reference specification sections when implementing features

### Quality First
- Don't skip testing or documentation
- Ensure CI/CD passes for all commits
- Maintain code coverage above 70%
- Regular refactoring and optimization

### User-Centered Design
- Prioritize responsive, intuitive interface
- Clear visual feedback for all operations
- Comprehensive help documentation
- Thoughtful error messages

### Professional Standards
- Production-ready code quality
- Enterprise-grade testing and CI/CD
- Comprehensive documentation
- Sustainable development practices

---

**Document Version:** 1.0
**Project:** SenseTop - Sense HAT Monitoring Application
**Target Platform:** Raspberry Pi 5 with Sense HAT
**Status:** Specification Phase
