"""LED Matrix Display Manager for Sense HAT.

This module provides control over the 8x8 RGB LED matrix on the Sense HAT,
including text scrolling, animations, and various display modes.
"""

import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from sense_hat import SenseHat
except ImportError:
    SenseHat = None  # Will use mock for testing


class LEDMode(Enum):
    """LED display modes."""

    OFF = "off"
    TEXT_SCROLL = "text_scroll"
    WORM_ANIMATION = "worm_animation"


class ColorMode(Enum):
    """Color modes for LED displays."""

    SOLID = "solid"
    CUSTOM_RGB = "custom_rgb"
    RAINBOW = "rainbow"
    GRADIENT = "gradient"


class ScrollSpeed(Enum):
    """Text scrolling speed."""

    SLOW = 0.15
    MEDIUM = 0.10
    FAST = 0.05


@dataclass
class LEDConfig:
    """LED display configuration."""

    mode: str = LEDMode.OFF.value
    brightness: float = 0.5  # 0.0 to 1.0
    fps: int = 30  # Refresh rate

    # Text scroll settings
    text: str = "SenseTop"
    scroll_speed: str = ScrollSpeed.MEDIUM.name
    text_color_mode: str = ColorMode.SOLID.value
    text_color: Tuple[int, int, int] = (255, 255, 255)  # White

    # Worm animation settings
    worm_speed: int = 5  # 1-10 scale
    worm_color_mode: str = "rainbow"
    worm_colors: List[Tuple[int, int, int]] = None  # 6 colors for segments

    def __post_init__(self) -> None:
        """Initialize default worm colors if not set."""
        if self.worm_colors is None:
            # Default rainbow colors (ROYGBV)
            self.worm_colors = [
                (255, 0, 0),  # Red
                (255, 127, 0),  # Orange
                (255, 255, 0),  # Yellow
                (0, 255, 0),  # Green
                (0, 0, 255),  # Blue
                (139, 0, 255),  # Violet
            ]

    @classmethod
    def load_from_file(cls, config_path: Path) -> "LEDConfig":
        """Load configuration from JSON file.

        Args:
            config_path: Path to configuration file.

        Returns:
            LEDConfig instance.
        """
        if not config_path.exists():
            return cls()

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls(**data)
        except Exception as e:
            logging.warning(f"Failed to load LED config: {e}, using defaults")
            return cls()

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to JSON file.

        Args:
            config_path: Path to configuration file.
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save LED config: {e}")


class LEDDisplayMode(ABC):
    """Abstract base class for LED display modes."""

    def __init__(self, sense_hat: Optional[SenseHat], config: LEDConfig) -> None:
        """Initialize the display mode.

        Args:
            sense_hat: Sense HAT instance (None for mock).
            config: LED configuration.
        """
        self.sense_hat = sense_hat
        self.config = config
        self.running = False
        self.logger = logging.getLogger(f"sensetop.led.{self.__class__.__name__}")

    @abstractmethod
    def update(self) -> None:
        """Update the LED display for one frame.

        This method is called repeatedly by the LED manager thread.
        """

    @abstractmethod
    def get_ascii_preview(self) -> str:
        """Get ASCII representation of current LED state.

        Returns:
            Multi-line string showing 8x8 grid.
        """

    def clear(self) -> None:
        """Clear the LED matrix."""
        if self.sense_hat:
            self.sense_hat.clear()

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Set a single pixel color.

        Args:
            x: X coordinate (0-7).
            y: Y coordinate (0-7).
            color: RGB color tuple (0-255 each).
        """
        if self.sense_hat:
            # Apply brightness
            r, g, b = color
            brightness = self.config.brightness
            color = (
                int(r * brightness),
                int(g * brightness),
                int(b * brightness),
            )
            self.sense_hat.set_pixel(x, y, color)

    def set_pixels(self, pixels: List[List[int]]) -> None:
        """Set all pixels at once.

        Args:
            pixels: 8x8 list of RGB values.
        """
        if self.sense_hat:
            # Apply brightness to all pixels
            brightness = self.config.brightness
            adjusted = []
            for pixel in pixels:
                if len(pixel) == 3:
                    r, g, b = pixel
                    adjusted.append(
                        [
                            int(r * brightness),
                            int(g * brightness),
                            int(b * brightness),
                        ]
                    )
                else:
                    adjusted.append(pixel)
            self.sense_hat.set_pixels(adjusted)


def generate_spiral_path() -> List[Tuple[int, int]]:
    """Generate clockwise spiral path from outer edge to center.

    The path starts at the top-right corner and spirals clockwise inward,
    covering all 64 pixels of the 8x8 matrix.

    Returns:
        List of (x, y) coordinates in spiral order.
    """
    path = []
    size = 8

    # Start from outer ring and work inward
    left, top, right, bottom = 0, 0, size - 1, size - 1

    while left <= right and top <= bottom:
        # Top edge: left to right
        for x in range(left, right + 1):
            path.append((x, top))
        top += 1

        # Right edge: top to bottom
        for y in range(top, bottom + 1):
            path.append((right, y))
        right -= 1

        # Bottom edge: right to left
        if top <= bottom:
            for x in range(right, left - 1, -1):
                path.append((x, bottom))
            bottom -= 1

        # Left edge: bottom to top
        if left <= right:
            for y in range(bottom, top - 1, -1):
                path.append((left, y))
            left += 1

    return path


class WormAnimationMode(LEDDisplayMode):
    """Worm animation that spirals from outer edge to center."""

    def __init__(self, sense_hat: Optional[SenseHat], config: LEDConfig) -> None:
        """Initialize worm animation.

        Args:
            sense_hat: Sense HAT instance.
            config: LED configuration.
        """
        super().__init__(sense_hat, config)
        self.spiral_path = generate_spiral_path()
        self.worm_length = 6
        self.position = 0  # Current head position in spiral
        self.frame_delay = (11 - config.worm_speed) / 10.0  # Convert 1-10 to delay
        self.last_update = 0.0

    def update(self) -> None:
        """Update worm animation for one frame."""
        current_time = time.time()

        # Check if enough time has passed for next frame
        if current_time - self.last_update < self.frame_delay:
            return

        self.last_update = current_time

        # Clear display
        self.clear()

        # Draw worm segments
        for i in range(self.worm_length):
            segment_pos = (self.position - i) % len(self.spiral_path)
            x, y = self.spiral_path[segment_pos]

            # Get color for this segment
            color = self._get_segment_color(i)
            self.set_pixel(x, y, color)

        # Advance position
        self.position = (self.position + 1) % len(self.spiral_path)

    def _get_segment_color(self, segment_index: int) -> Tuple[int, int, int]:
        """Get color for a specific worm segment.

        Args:
            segment_index: Index of segment (0 = head, 5 = tail).

        Returns:
            RGB color tuple.
        """
        if self.config.worm_color_mode == "rainbow":
            return self.config.worm_colors[segment_index]
        elif self.config.worm_color_mode == "custom":
            return self.config.worm_colors[segment_index]
        else:
            # Themed palettes can be added here
            return self.config.worm_colors[segment_index]

    def get_ascii_preview(self) -> str:
        """Get ASCII representation of current worm state.

        Returns:
            8x8 ASCII grid showing worm position.
        """
        grid = [["·" for _ in range(8)] for _ in range(8)]

        # Draw worm segments
        for i in range(self.worm_length):
            segment_pos = (self.position - i) % len(self.spiral_path)
            x, y = self.spiral_path[segment_pos]
            grid[y][x] = "█"

        return "\n".join("".join(row) for row in grid)


class TextScrollMode(LEDDisplayMode):
    """Text scrolling display mode."""

    def __init__(self, sense_hat: Optional[SenseHat], config: LEDConfig) -> None:
        """Initialize text scroll mode.

        Args:
            sense_hat: Sense HAT instance.
            config: LED configuration.
        """
        super().__init__(sense_hat, config)
        self.scroll_thread: Optional[threading.Thread] = None
        self.scrolling = False

    def start_scrolling(self) -> None:
        """Start the text scrolling in a separate thread."""
        if self.scrolling:
            return

        self.scrolling = True
        self.scroll_thread = threading.Thread(target=self._scroll_text_loop, daemon=True)
        self.scroll_thread.start()

    def stop_scrolling(self) -> None:
        """Stop the text scrolling."""
        self.scrolling = False
        if self.scroll_thread:
            self.scroll_thread.join(timeout=1.0)

    def _scroll_text_loop(self) -> None:
        """Continuously scroll text on the LED matrix."""
        if not self.sense_hat:
            return

        scroll_speed = ScrollSpeed[self.config.scroll_speed].value
        color = self._get_text_color()

        while self.scrolling:
            try:
                # Use Sense HAT's show_message with non-blocking approach
                # We use a very fast scroll speed and loop to give continuous effect
                self.sense_hat.show_message(
                    self.config.text,
                    scroll_speed=scroll_speed,
                    text_colour=color,
                    back_colour=[0, 0, 0],
                )
            except Exception as e:
                self.logger.error(f"Error scrolling text: {e}")
                break

    def update(self) -> None:
        """Update text scroll for one frame."""
        # Start scrolling if not already started
        if not self.scrolling:
            self.start_scrolling()

    def _get_text_color(self) -> Tuple[int, int, int]:
        """Get color for text based on color mode.

        Returns:
            RGB color tuple.
        """
        if self.config.text_color_mode == ColorMode.SOLID.value:
            return self.config.text_color
        elif self.config.text_color_mode == ColorMode.RAINBOW.value:
            # Rainbow color cycles based on position
            hue = (self.scroll_position * 10) % 360
            return self._hue_to_rgb(hue)
        else:
            return self.config.text_color

    def _hue_to_rgb(self, hue: float) -> Tuple[int, int, int]:
        """Convert HSV hue to RGB color.

        Args:
            hue: Hue value (0-360).

        Returns:
            RGB color tuple (0-255).
        """
        h = hue / 60.0
        x = int(255 * (1 - abs(h % 2 - 1)))

        if 0 <= h < 1:
            return (255, x, 0)
        elif 1 <= h < 2:
            return (x, 255, 0)
        elif 2 <= h < 3:
            return (0, 255, x)
        elif 3 <= h < 4:
            return (0, x, 255)
        elif 4 <= h < 5:
            return (x, 0, 255)
        else:
            return (255, 0, x)

    def clear(self) -> None:
        """Clear the LED matrix and stop scrolling."""
        self.stop_scrolling()
        super().clear()

    def get_ascii_preview(self) -> str:
        """Get ASCII representation of scrolling text.

        Returns:
            8x8 ASCII grid showing text info.
        """
        # Show text preview - first few characters
        grid = [["·" for _ in range(8)] for _ in range(8)]

        # Display text indicator in center
        text_preview = self.config.text[:8] if self.config.text else "TEXT"
        for i, char in enumerate(text_preview):
            if i < 8:
                grid[4][i] = char if char.isprintable() else "?"

        return "\n".join("".join(row) for row in grid)


class LEDDisplayManager:
    """Manager for LED matrix display modes and animations."""

    def __init__(self, use_mock: bool = False, config_path: Optional[Path] = None) -> None:
        """Initialize LED display manager.

        Args:
            use_mock: Use mock Sense HAT for testing.
            config_path: Path to configuration file.
        """
        self.logger = logging.getLogger("sensetop.led")

        # Load configuration
        if config_path is None:
            config_path = Path.home() / ".sensetop" / "led_config.json"
        self.config_path = config_path
        self.config = LEDConfig.load_from_file(config_path)

        # Initialize Sense HAT
        self.sense_hat = None
        if not use_mock:
            try:
                if SenseHat is not None:
                    self.sense_hat = SenseHat()
                    self.sense_hat.low_light = self.config.brightness < 0.3
                    self.logger.info("Initialized Sense HAT LED matrix")
            except Exception as e:
                self.logger.error(f"Failed to initialize Sense HAT: {e}")

        # Display mode
        self.current_mode: Optional[LEDDisplayMode] = None
        self.set_mode(LEDMode[self.config.mode.upper()])

        # Update thread
        self.running = False
        self.update_thread: Optional[threading.Thread] = None

    def set_mode(self, mode: LEDMode) -> None:
        """Set the current display mode.

        Args:
            mode: LED mode to activate.
        """
        # Stop current mode
        if self.current_mode:
            self.current_mode.clear()

        # Create new mode
        if mode == LEDMode.OFF:
            self.current_mode = None
            if self.sense_hat:
                self.sense_hat.clear()
        elif mode == LEDMode.TEXT_SCROLL:
            self.current_mode = TextScrollMode(self.sense_hat, self.config)
        elif mode == LEDMode.WORM_ANIMATION:
            self.current_mode = WormAnimationMode(self.sense_hat, self.config)

        self.config.mode = mode.value
        self.logger.info(f"LED mode set to: {mode.value}")

    def start(self) -> None:
        """Start the LED update thread."""
        if self.running:
            return

        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        self.logger.info("LED update thread started")

    def stop(self) -> None:
        """Stop the LED update thread."""
        if not self.running:
            return

        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)

        # Clear display
        if self.sense_hat:
            self.sense_hat.clear()

        self.logger.info("LED update thread stopped")

    def _update_loop(self) -> None:
        """Main update loop running in background thread."""
        frame_time = 1.0 / self.config.fps

        while self.running:
            try:
                if self.current_mode:
                    self.current_mode.update()
                time.sleep(frame_time)
            except Exception as e:
                self.logger.error(f"Error in LED update loop: {e}", exc_info=True)

    def get_ascii_preview(self) -> str:
        """Get ASCII preview of current LED state.

        Returns:
            Multi-line string showing 8x8 grid.
        """
        if self.current_mode:
            return self.current_mode.get_ascii_preview()
        else:
            # Off mode: show empty grid
            return "\n".join("·" * 8 for _ in range(8))

    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config.save_to_file(self.config_path)
        self.logger.info(f"LED config saved to {self.config_path}")

    def shutdown(self) -> None:
        """Shutdown the LED manager and clean up."""
        self.stop()
        self.save_config()
        self.logger.info("LED manager shutdown complete")
