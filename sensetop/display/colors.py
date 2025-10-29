"""Color scheme management for the TUI."""

import curses
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple


class ColorPair(Enum):
    """Color pair identifiers for curses."""

    DEFAULT = 1
    HEADER = 2
    STATUS_OK = 3
    STATUS_WARNING = 4
    STATUS_ERROR = 5
    STATUS_CRITICAL = 6
    BORDER = 7
    LABEL = 8
    VALUE = 9
    HIGHLIGHT = 10
    FOOTER = 11
    INACTIVE = 12


@dataclass
class ColorScheme:
    """Color scheme definition for the terminal UI."""

    name: str
    description: str
    colors: Dict[ColorPair, Tuple[int, int]]  # (foreground, background)


class ColorManager:
    """Manages color schemes and curses color pairs."""

    # Built-in color schemes
    DARK_SCHEME = ColorScheme(
        name="dark",
        description="Dark theme (black background)",
        colors={
            ColorPair.DEFAULT: (curses.COLOR_WHITE, curses.COLOR_BLACK),
            ColorPair.HEADER: (curses.COLOR_CYAN, curses.COLOR_BLACK),
            ColorPair.STATUS_OK: (curses.COLOR_GREEN, curses.COLOR_BLACK),
            ColorPair.STATUS_WARNING: (curses.COLOR_YELLOW, curses.COLOR_BLACK),
            ColorPair.STATUS_ERROR: (curses.COLOR_RED, curses.COLOR_BLACK),
            ColorPair.STATUS_CRITICAL: (curses.COLOR_WHITE, curses.COLOR_RED),
            ColorPair.BORDER: (curses.COLOR_CYAN, curses.COLOR_BLACK),
            ColorPair.LABEL: (curses.COLOR_CYAN, curses.COLOR_BLACK),
            ColorPair.VALUE: (curses.COLOR_WHITE, curses.COLOR_BLACK),
            ColorPair.HIGHLIGHT: (curses.COLOR_BLACK, curses.COLOR_CYAN),
            ColorPair.FOOTER: (curses.COLOR_WHITE, curses.COLOR_BLACK),
            ColorPair.INACTIVE: (curses.COLOR_BLACK, curses.COLOR_BLACK),
        },
    )

    LIGHT_SCHEME = ColorScheme(
        name="light",
        description="Light theme (white background)",
        colors={
            ColorPair.DEFAULT: (curses.COLOR_BLACK, curses.COLOR_WHITE),
            ColorPair.HEADER: (curses.COLOR_BLUE, curses.COLOR_WHITE),
            ColorPair.STATUS_OK: (curses.COLOR_GREEN, curses.COLOR_WHITE),
            ColorPair.STATUS_WARNING: (curses.COLOR_RED, curses.COLOR_WHITE),
            ColorPair.STATUS_ERROR: (curses.COLOR_RED, curses.COLOR_WHITE),
            ColorPair.STATUS_CRITICAL: (curses.COLOR_WHITE, curses.COLOR_RED),
            ColorPair.BORDER: (curses.COLOR_BLUE, curses.COLOR_WHITE),
            ColorPair.LABEL: (curses.COLOR_BLUE, curses.COLOR_WHITE),
            ColorPair.VALUE: (curses.COLOR_BLACK, curses.COLOR_WHITE),
            ColorPair.HIGHLIGHT: (curses.COLOR_WHITE, curses.COLOR_BLUE),
            ColorPair.FOOTER: (curses.COLOR_BLACK, curses.COLOR_WHITE),
            ColorPair.INACTIVE: (curses.COLOR_WHITE, curses.COLOR_WHITE),
        },
    )

    COLORFUL_SCHEME = ColorScheme(
        name="colorful",
        description="Colorful theme with vibrant colors",
        colors={
            ColorPair.DEFAULT: (curses.COLOR_WHITE, curses.COLOR_BLUE),
            ColorPair.HEADER: (curses.COLOR_YELLOW, curses.COLOR_BLUE),
            ColorPair.STATUS_OK: (curses.COLOR_GREEN, curses.COLOR_BLUE),
            ColorPair.STATUS_WARNING: (curses.COLOR_YELLOW, curses.COLOR_BLUE),
            ColorPair.STATUS_ERROR: (curses.COLOR_RED, curses.COLOR_BLUE),
            ColorPair.STATUS_CRITICAL: (curses.COLOR_YELLOW, curses.COLOR_RED),
            ColorPair.BORDER: (curses.COLOR_CYAN, curses.COLOR_BLUE),
            ColorPair.LABEL: (curses.COLOR_MAGENTA, curses.COLOR_BLUE),
            ColorPair.VALUE: (curses.COLOR_WHITE, curses.COLOR_BLUE),
            ColorPair.HIGHLIGHT: (curses.COLOR_BLACK, curses.COLOR_YELLOW),
            ColorPair.FOOTER: (curses.COLOR_WHITE, curses.COLOR_BLUE),
            ColorPair.INACTIVE: (curses.COLOR_BLUE, curses.COLOR_BLUE),
        },
    )

    def __init__(self, scheme: Optional[ColorScheme] = None) -> None:
        """Initialize color manager with a color scheme.

        Args:
            scheme: Color scheme to use. Defaults to DARK_SCHEME.
        """
        self.scheme = scheme or self.DARK_SCHEME
        self.color_pairs: Dict[ColorPair, int] = {}

    def initialize(self) -> None:
        """Initialize curses color pairs.

        Must be called after curses.initscr() and before drawing.
        """
        # Check if terminal supports colors
        if not curses.has_colors():
            raise RuntimeError("Terminal does not support colors")

        # Initialize color pairs
        pair_id = 1
        for color_pair, (fg, bg) in self.scheme.colors.items():
            curses.init_pair(pair_id, fg, bg)
            self.color_pairs[color_pair] = pair_id
            pair_id += 1

    def get_pair(self, color_pair: ColorPair) -> int:
        """Get the curses color pair ID.

        Args:
            color_pair: The color pair enum value.

        Returns:
            The curses color pair ID.

        Raises:
            RuntimeError: If colors not initialized or pair not found.
        """
        if not self.color_pairs:
            raise RuntimeError("Colors not initialized. Call initialize() first.")

        if color_pair not in self.color_pairs:
            raise ValueError(f"Unknown color pair: {color_pair}")

        return self.color_pairs[color_pair]

    def get_attr(self, color_pair: ColorPair) -> int:
        """Get curses attributes with color.

        Args:
            color_pair: The color pair enum value.

        Returns:
            Curses color pair attributes.
        """
        return curses.color_pair(self.get_pair(color_pair))

    @classmethod
    def get_available_schemes(cls) -> Dict[str, ColorScheme]:
        """Get all available color schemes.

        Returns:
            Dictionary of available color schemes.
        """
        return {
            cls.DARK_SCHEME.name: cls.DARK_SCHEME,
            cls.LIGHT_SCHEME.name: cls.LIGHT_SCHEME,
            cls.COLORFUL_SCHEME.name: cls.COLORFUL_SCHEME,
        }
