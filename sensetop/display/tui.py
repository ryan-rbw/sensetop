"""Terminal UI framework using curses."""

import curses
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from sensetop.display.colors import ColorManager, ColorScheme


class UIView(ABC):
    """Abstract base class for UI views."""

    def __init__(self, name: str, color_manager: ColorManager) -> None:
        """Initialize a UI view.

        Args:
            name: Name of the view.
            color_manager: Color manager instance.
        """
        self.name = name
        self.color_manager = color_manager

    @abstractmethod
    def draw(self, stdscr: "curses._CursesWindow") -> None:
        """Draw the view on the screen.

        Args:
            stdscr: Curses window object.
        """

    @abstractmethod
    def handle_input(self, key: int) -> bool:
        """Handle keyboard input.

        Args:
            key: The keyboard key code.

        Returns:
            True if key was handled, False otherwise.
        """


class TUI:
    """Terminal User Interface manager."""

    def __init__(
        self,
        color_scheme: Optional[ColorScheme] = None,
        refresh_rate: int = 500,  # milliseconds
    ) -> None:
        """Initialize TUI.

        Args:
            color_scheme: Color scheme to use.
            refresh_rate: Screen refresh rate in milliseconds.
        """
        self.color_manager = ColorManager(color_scheme)
        self.refresh_rate = refresh_rate
        self.stdscr: Optional["curses._CursesWindow"] = None
        self.running = False
        self.current_view: Optional[UIView] = None
        self.views: dict[str, UIView] = {}

    def register_view(self, view: UIView) -> None:
        """Register a UI view.

        Args:
            view: The view to register.
        """
        self.views[view.name] = view

    def set_current_view(self, view_name: str) -> None:
        """Set the current active view.

        Args:
            view_name: Name of the view to activate.

        Raises:
            ValueError: If view not found.
        """
        if view_name not in self.views:
            raise ValueError(f"View not found: {view_name}")

        self.current_view = self.views[view_name]

    def initialize(self, stdscr: "curses._CursesWindow") -> None:
        """Initialize curses and color schemes.

        Args:
            stdscr: The curses window.
        """
        self.stdscr = stdscr

        # Configure curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(self.refresh_rate)  # Refresh timeout

        # Initialize colors
        self.color_manager.initialize()

    def draw(self) -> None:
        """Draw the current view."""
        if self.stdscr is None or self.current_view is None:
            return

        try:
            self.stdscr.clear()
            self.current_view.draw(self.stdscr)
            self.stdscr.refresh()
        except curses.error:
            # Handle curses errors gracefully
            pass

    def handle_input(self, key: int) -> bool:
        """Handle keyboard input.

        Args:
            key: The keyboard key code.

        Returns:
            True if key was handled and should continue, False to exit.
        """
        if key == -1:  # No input
            return True

        if key == ord("q") or key == 27:  # 'q' or ESC to quit
            return False

        if key == ord("h") or key == ord("?"):  # Help
            if "help" in self.views:
                self.set_current_view("help")
            return True

        # View switching with numeric keys
        if key == ord("1"):  # Dashboard
            if "dashboard" in self.views:
                self.set_current_view("dashboard")
            return True

        if key == ord("2"):  # Settings (placeholder)
            if "settings" in self.views:
                self.set_current_view("settings")
            return True

        if key == ord("3"):  # About (placeholder)
            if "about" in self.views:
                self.set_current_view("about")
            return True

        # Let the current view handle the input
        if self.current_view:
            result = self.current_view.handle_input(key)
            # If view returns False, try to return to dashboard
            if not result and "dashboard" in self.views:
                self.set_current_view("dashboard")

        return True

    def get_screen_size(self) -> Tuple[int, int]:
        """Get the screen size.

        Returns:
            Tuple of (height, width).
        """
        if self.stdscr is None:
            return (0, 0)

        return self.stdscr.getmaxyx()

    def shutdown(self) -> None:
        """Shutdown the TUI and restore terminal."""
        if self.stdscr is not None:
            try:
                self.stdscr.clear()
                self.stdscr.refresh()
            except curses.error:
                pass
