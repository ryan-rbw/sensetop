"""Configuration management for SenseTop."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class Config:
    """Configuration for SenseTop application."""

    # Display settings
    theme: str = "dark"  # dark, light, colorful
    refresh_rate: int = 500  # milliseconds
    color_support: bool = True
    enable_logging: bool = True

    # Sensor settings
    use_mock: bool = False  # Use mock sensors for testing
    sensor_interval: int = 500  # milliseconds between sensor reads
    i2c_bus: int = 1  # I2C bus number (Raspberry Pi default)

    # Data collection
    buffer_size: int = 120  # Number of historical data points to keep
    enable_data_export: bool = True

    # File paths
    log_file: str = field(default_factory=lambda: str(Path.home() / ".sensetop" / "sensetop.log"))
    config_file: str = field(default_factory=lambda: str(Path.home() / ".sensetop" / "config.json"))
    data_dir: str = field(default_factory=lambda: str(Path.home() / ".sensetop" / "data"))

    # Display options
    show_graph: bool = True
    graph_type: str = "ascii"  # ascii or unicode
    decimal_places: int = 2

    # Temperature unit
    temperature_unit: str = "celsius"  # celsius or fahrenheit

    # Pressure unit
    pressure_unit: str = "hpa"  # hpa, mmhg, inhg

    @classmethod
    def load(cls, config_file: Optional[str] = None) -> "Config":
        """Load configuration from file.

        Args:
            config_file: Path to config file. Uses default if None.

        Returns:
            Config instance.
        """
        if config_file is None:
            config_file = str(Path.home() / ".sensetop" / "config.json")

        config_path = Path(config_file)

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
                return cls()

        return cls()

    def save(self, config_file: Optional[str] = None) -> None:
        """Save configuration to file.

        Args:
            config_file: Path to config file. Uses default if None.
        """
        if config_file is None:
            config_file = self.config_file

        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of config.
        """
        return asdict(self)

    def __post_init__(self) -> None:
        """Post-initialization setup."""
        # Create data directories
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
