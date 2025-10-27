# SenseTop

A real-time monitoring application for the Sense HAT module on Raspberry Pi 5, providing a terminal-based interface similar to HTOP or JTOP. It displays sensor data, environmental metrics, and system configuration in an interactive dashboard with live updates.

## Features

- **Real-Time Sensor Monitoring**: Temperature, humidity, pressure, and motion/orientation data
- **Interactive Dashboard**: Color-coded status indicators and historical graphs
- **System Metrics**: CPU usage, memory, uptime, and network information
- **Data Export**: CSV export for sensor readings
- **Keyboard Navigation**: Intuitive controls for menu navigation and configuration

## Hardware Requirements

- Raspberry Pi 5 with 4GB RAM (8GB recommended)
- Sense HAT module properly installed
- I2C enabled on Raspberry Pi
- Python 3.8+

## Quick Start

### Installation

Clone the repository and set up the environment:

```bash
git clone https://github.com/ryan-rbw/sensetop.git
cd sensetop
./scripts/setup.sh
```

### Running

```bash
python -m sensetop
```

Or use the systemd service:

```bash
sudo systemctl start sensetop
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [User Guide](docs/USER_GUIDE.md) - Keyboard shortcuts and features
- [API Documentation](docs/API.md) - Module and function reference
- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## Development

See [SPEC.md](SPEC.md) for the complete project specification and development guidelines.

### Running Tests

```bash
make test
```

### Code Quality Checks

```bash
make lint
```

### Building

```bash
make build
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

---

**Status**: Development Phase
**Target Platform**: Raspberry Pi 5 with Sense HAT
**Latest Version**: 0.1.0-dev
