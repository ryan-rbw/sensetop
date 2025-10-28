"""Unit tests for display components."""

import pytest

from sensetop.display.colors import ColorManager, ColorPair, ColorScheme
from sensetop.display.tui import TUI, UIView
from sensetop.display.views import HelpView


class MockView(UIView):
    """Mock view for testing."""

    def __init__(self, name: str, color_manager: ColorManager) -> None:
        """Initialize mock view."""
        super().__init__(name, color_manager)
        self.draw_called = False
        self.input_handled = False

    def draw(self, stdscr) -> None:
        """Record that draw was called."""
        self.draw_called = True

    def handle_input(self, key: int) -> bool:
        """Record that input was handled."""
        self.input_handled = True
        return True


class TestColorManager:
    """Tests for color management."""

    def test_color_schemes_available(self):
        """Test that all color schemes are available."""
        schemes = ColorManager.get_available_schemes()
        assert "dark" in schemes
        assert "light" in schemes
        assert "colorful" in schemes

    def test_default_color_manager(self):
        """Test default color manager initialization."""
        cm = ColorManager()
        assert cm.scheme == ColorManager.DARK_SCHEME

    def test_custom_color_scheme(self):
        """Test color manager with custom scheme."""
        cm = ColorManager(ColorManager.LIGHT_SCHEME)
        assert cm.scheme == ColorManager.LIGHT_SCHEME

    def test_color_pair_enum(self):
        """Test color pair enum values."""
        assert isinstance(ColorPair.DEFAULT, ColorPair)
        assert isinstance(ColorPair.HEADER, ColorPair)
        assert isinstance(ColorPair.STATUS_OK, ColorPair)


class TestTUI:
    """Tests for TUI framework."""

    def test_tui_initialization(self):
        """Test TUI initialization."""
        tui = TUI()
        assert tui.running is False
        assert tui.current_view is None
        assert len(tui.views) == 0

    def test_register_view(self):
        """Test registering a view."""
        tui = TUI()
        color_manager = ColorManager()
        view = MockView("test", color_manager)

        tui.register_view(view)
        assert "test" in tui.views
        assert tui.views["test"] == view

    def test_set_current_view(self):
        """Test setting the current view."""
        tui = TUI()
        color_manager = ColorManager()
        view = MockView("test", color_manager)

        tui.register_view(view)
        tui.set_current_view("test")
        assert tui.current_view == view

    def test_set_invalid_view(self):
        """Test setting an invalid view raises error."""
        tui = TUI()
        with pytest.raises(ValueError):
            tui.set_current_view("nonexistent")

    def test_handle_quit_key(self):
        """Test that 'q' key quits the application."""
        tui = TUI()
        result = tui.handle_input(ord("q"))
        assert result is False

    def test_handle_escape_key(self):
        """Test that ESC key quits the application."""
        tui = TUI()
        result = tui.handle_input(27)  # ESC
        assert result is False

    def test_handle_no_input(self):
        """Test handling no input."""
        tui = TUI()
        result = tui.handle_input(-1)
        assert result is True

    def test_screen_size(self):
        """Test getting screen size without initialization."""
        tui = TUI()
        height, width = tui.get_screen_size()
        assert height == 0
        assert width == 0

    def test_refresh_rate_default(self):
        """Test default refresh rate."""
        tui = TUI()
        assert tui.refresh_rate == 500

    def test_custom_refresh_rate(self):
        """Test custom refresh rate."""
        tui = TUI(refresh_rate=1000)
        assert tui.refresh_rate == 1000


class TestUIView:
    """Tests for base UIView class."""

    def test_uiview_initialization(self):
        """Test UIView initialization."""
        color_manager = ColorManager()
        view = MockView("test_view", color_manager)

        assert view.name == "test_view"
        assert view.color_manager == color_manager

    def test_uiview_draw(self):
        """Test that draw method can be called."""
        color_manager = ColorManager()
        view = MockView("test_view", color_manager)

        view.draw(None)  # type: ignore
        assert view.draw_called is True

    def test_uiview_handle_input(self):
        """Test that handle_input method can be called."""
        color_manager = ColorManager()
        view = MockView("test_view", color_manager)

        result = view.handle_input(ord("a"))
        assert result is True
        assert view.input_handled is True


class TestColorSchemes:
    """Tests for color scheme definitions."""

    def test_dark_scheme_colors(self):
        """Test dark scheme has all required colors."""
        scheme = ColorManager.DARK_SCHEME
        assert len(scheme.colors) > 0

        # Check that all ColorPair enum values are in the scheme
        for color_pair in ColorPair:
            assert color_pair in scheme.colors

    def test_light_scheme_colors(self):
        """Test light scheme has all required colors."""
        scheme = ColorManager.LIGHT_SCHEME
        assert len(scheme.colors) > 0

        # Check that all ColorPair enum values are in the scheme
        for color_pair in ColorPair:
            assert color_pair in scheme.colors

    def test_colorful_scheme_colors(self):
        """Test colorful scheme has all required colors."""
        scheme = ColorManager.COLORFUL_SCHEME
        assert len(scheme.colors) > 0

        # Check that all ColorPair enum values are in the scheme
        for color_pair in ColorPair:
            assert color_pair in scheme.colors

    def test_color_tuple_format(self):
        """Test that color pairs are in correct format."""
        scheme = ColorManager.DARK_SCHEME

        for color_pair, colors in scheme.colors.items():
            # Each color pair should be a tuple of (fg, bg)
            assert isinstance(colors, tuple)
            assert len(colors) == 2
            fg, bg = colors
            # Colors should be valid curses color constants
            assert fg >= 0
            assert bg >= 0


class TestHelpView:
    """Tests for help view."""

    def test_help_view_initialization(self):
        """Test HelpView initialization."""
        color_manager = ColorManager()
        help_view = HelpView("help", color_manager)

        assert help_view.name == "help"
        assert help_view.color_manager == color_manager
        assert len(help_view.help_text) > 0

    def test_help_view_draw(self):
        """Test that help view can be drawn."""
        color_manager = ColorManager()
        help_view = HelpView("help", color_manager)

        help_view.draw(None)  # type: ignore
        # If no exception, test passes

    def test_help_view_handle_input_no_key(self):
        """Test help view with no input."""
        color_manager = ColorManager()
        help_view = HelpView("help", color_manager)

        result = help_view.handle_input(-1)
        assert result is True

    def test_help_view_handle_input_key(self):
        """Test help view returns to dashboard on any key."""
        color_manager = ColorManager()
        help_view = HelpView("help", color_manager)

        result = help_view.handle_input(ord("a"))
        assert result is False


class TestTUIViewNavigation:
    """Tests for TUI view navigation."""

    def test_tui_help_view_navigation(self):
        """Test navigating to help view."""
        tui = TUI()
        color_manager = ColorManager()

        dashboard = MockView("dashboard", color_manager)
        help_view = HelpView("help", color_manager)

        tui.register_view(dashboard)
        tui.register_view(help_view)
        tui.set_current_view("dashboard")

        # Press 'h' to go to help
        result = tui.handle_input(ord("h"))
        assert result is True
        assert tui.current_view == help_view

    def test_tui_numeric_view_switching(self):
        """Test numeric key view switching."""
        tui = TUI()
        color_manager = ColorManager()

        view1 = MockView("dashboard", color_manager)
        view2 = MockView("graphs", color_manager)
        view3 = MockView("about", color_manager)

        tui.register_view(view1)
        tui.register_view(view2)
        tui.register_view(view3)
        tui.set_current_view("dashboard")

        # Press '1' to stay on dashboard
        tui.handle_input(ord("1"))
        assert tui.current_view == view1

        # Press '2' to switch to graphs
        tui.handle_input(ord("2"))
        assert tui.current_view == view2

        # Press '3' to switch to about
        tui.handle_input(ord("3"))
        assert tui.current_view == view3

    def test_tui_return_from_help(self):
        """Test returning to dashboard from help view."""
        tui = TUI()
        color_manager = ColorManager()

        dashboard = MockView("dashboard", color_manager)
        help_view = HelpView("help", color_manager)

        tui.register_view(dashboard)
        tui.register_view(help_view)
        tui.set_current_view("dashboard")

        # Go to help
        tui.handle_input(ord("h"))
        assert tui.current_view == help_view

        # Simulate pressing a key in help (which returns False)
        # This should trigger return to dashboard
        result = help_view.handle_input(ord("a"))
        assert result is False

    def test_tui_question_mark_for_help(self):
        """Test that '?' also opens help."""
        tui = TUI()
        color_manager = ColorManager()

        dashboard = MockView("dashboard", color_manager)
        help_view = HelpView("help", color_manager)

        tui.register_view(dashboard)
        tui.register_view(help_view)
        tui.set_current_view("dashboard")

        # Press '?' to go to help
        result = tui.handle_input(ord("?"))
        assert result is True
        assert tui.current_view == help_view
