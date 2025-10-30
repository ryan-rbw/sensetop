"""Tests for LED display manager."""

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from sensetop.display.led_manager import (
    ColorMode,
    LEDConfig,
    LEDDisplayManager,
    LEDMode,
    ScrollSpeed,
    TextScrollMode,
    WormAnimationMode,
    generate_spiral_path,
)


class TestLEDConfig:
    """Tests for LEDConfig dataclass."""

    def test_led_config_defaults(self):
        """Test LED config has correct defaults."""
        config = LEDConfig()
        assert config.mode == LEDMode.OFF.value
        assert config.brightness == 0.5
        assert config.fps == 30
        assert config.text == "SenseTop"
        assert config.scroll_speed == ScrollSpeed.MEDIUM.name
        assert config.text_color_mode == ColorMode.SOLID.value
        assert config.text_color == (255, 255, 255)
        assert config.worm_speed == 5
        assert config.worm_color_mode == "rainbow"
        assert len(config.worm_colors) == 6

    def test_led_config_custom_values(self):
        """Test LED config with custom values."""
        config = LEDConfig(
            mode=LEDMode.TEXT_SCROLL.value,
            brightness=0.8,
            text="Hello World",
            text_color=(255, 0, 0),
        )
        assert config.mode == LEDMode.TEXT_SCROLL.value
        assert config.brightness == 0.8
        assert config.text == "Hello World"
        assert config.text_color == (255, 0, 0)

    def test_led_config_save_load(self, tmp_path):
        """Test saving and loading LED config."""
        config_path = tmp_path / "led_config.json"

        # Create and save config
        config = LEDConfig(
            mode=LEDMode.WORM_ANIMATION.value,
            text="Test Message",
            brightness=0.75,
        )
        config.save_to_file(config_path)

        # Load config
        loaded_config = LEDConfig.load_from_file(config_path)
        assert loaded_config.mode == config.mode
        assert loaded_config.text == config.text
        assert loaded_config.brightness == config.brightness

    def test_led_config_load_missing_file(self, tmp_path):
        """Test loading config from missing file returns defaults."""
        config_path = tmp_path / "nonexistent.json"
        config = LEDConfig.load_from_file(config_path)
        assert config.mode == LEDMode.OFF.value

    def test_led_config_load_invalid_json(self, tmp_path):
        """Test loading config from invalid JSON returns defaults."""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("not valid json")
        config = LEDConfig.load_from_file(config_path)
        assert config.mode == LEDMode.OFF.value


class TestSpiralPath:
    """Tests for spiral path generation."""

    def test_generate_spiral_path_length(self):
        """Test spiral path has 64 pixels (8x8 matrix)."""
        path = generate_spiral_path()
        assert len(path) == 64

    def test_generate_spiral_path_all_unique(self):
        """Test spiral path covers all unique pixels."""
        path = generate_spiral_path()
        unique_positions = set(path)
        assert len(unique_positions) == 64

    def test_generate_spiral_path_valid_coordinates(self):
        """Test spiral path contains valid 8x8 coordinates."""
        path = generate_spiral_path()
        for x, y in path:
            assert 0 <= x < 8
            assert 0 <= y < 8

    def test_generate_spiral_path_starts_at_corner(self):
        """Test spiral path starts at top-left corner."""
        path = generate_spiral_path()
        assert path[0] == (0, 0)


class TestWormAnimationMode:
    """Tests for WormAnimationMode."""

    @pytest.fixture
    def mock_sense_hat(self):
        """Create mock Sense HAT."""
        mock = MagicMock()
        mock.set_pixel = MagicMock()
        mock.clear = MagicMock()
        mock.set_rotation = MagicMock()
        return mock

    @pytest.fixture
    def worm_config(self):
        """Create LED config for worm animation."""
        return LEDConfig(mode=LEDMode.WORM_ANIMATION.value, worm_speed=5)

    def test_worm_init(self, mock_sense_hat, worm_config):
        """Test worm animation initialization."""
        worm = WormAnimationMode(mock_sense_hat, worm_config)
        assert worm.sense_hat == mock_sense_hat
        assert worm.worm_length == 6
        assert worm.position == 0
        assert len(worm.spiral_path) == 64
        mock_sense_hat.set_rotation.assert_called_once_with(0)

    def test_worm_update(self, mock_sense_hat, worm_config):
        """Test worm animation update."""
        worm = WormAnimationMode(mock_sense_hat, worm_config)

        # First update should draw worm
        worm.update()
        assert mock_sense_hat.set_pixel.call_count == 6  # 6 segments

        # Position should advance
        initial_pos = worm.position
        worm.update()
        # Might not advance if not enough time passed
        assert worm.position >= initial_pos

    def test_worm_get_segment_color(self, mock_sense_hat, worm_config):
        """Test worm segment color retrieval."""
        worm = WormAnimationMode(mock_sense_hat, worm_config)
        color = worm._get_segment_color(0)
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)

    def test_worm_ascii_preview(self, mock_sense_hat, worm_config):
        """Test worm ASCII preview generation."""
        worm = WormAnimationMode(mock_sense_hat, worm_config)
        preview = worm.get_ascii_preview()
        assert isinstance(preview, str)
        lines = preview.split("\n")
        assert len(lines) == 8  # 8x8 grid
        assert all(len(line) == 8 for line in lines)

    def test_worm_clear(self, mock_sense_hat, worm_config):
        """Test worm clear method."""
        worm = WormAnimationMode(mock_sense_hat, worm_config)
        worm.clear()
        mock_sense_hat.clear.assert_called()


class TestTextScrollMode:
    """Tests for TextScrollMode."""

    @pytest.fixture
    def mock_sense_hat(self):
        """Create mock Sense HAT."""
        mock = MagicMock()
        mock.show_message = MagicMock()
        mock.clear = MagicMock()
        mock.set_rotation = MagicMock()
        return mock

    @pytest.fixture
    def text_config(self):
        """Create LED config for text scrolling."""
        return LEDConfig(
            mode=LEDMode.TEXT_SCROLL.value,
            text="Hello",
            scroll_speed=ScrollSpeed.FAST.name,
        )

    def test_text_init(self, mock_sense_hat, text_config):
        """Test text scroll mode initialization."""
        text_mode = TextScrollMode(mock_sense_hat, text_config)
        try:
            assert text_mode.sense_hat == mock_sense_hat
            assert text_mode.active is True
            mock_sense_hat.set_rotation.assert_called_once_with(0)
        finally:
            text_mode.clear()  # Stop thread

    def test_text_get_color_solid(self, mock_sense_hat, text_config):
        """Test text color retrieval for solid mode."""
        text_mode = TextScrollMode(mock_sense_hat, text_config)
        try:
            color = text_mode._get_text_color()
            assert color == text_config.text_color
        finally:
            text_mode.clear()

    def test_text_clear(self, mock_sense_hat, text_config):
        """Test text scroll mode clear."""
        text_mode = TextScrollMode(mock_sense_hat, text_config)
        text_mode.clear()
        assert text_mode.active is False
        mock_sense_hat.clear.assert_called()

    def test_text_ascii_preview(self, mock_sense_hat, text_config):
        """Test text ASCII preview generation."""
        text_mode = TextScrollMode(mock_sense_hat, text_config)
        try:
            preview = text_mode.get_ascii_preview()
            assert isinstance(preview, str)
            lines = preview.split("\n")
            assert len(lines) == 8
            # Should show first characters of text
            assert "Hello" in preview or "H" in preview
        finally:
            text_mode.clear()

    def test_text_update_does_nothing(self, mock_sense_hat, text_config):
        """Test text scroll update method (does nothing, thread handles scrolling)."""
        text_mode = TextScrollMode(mock_sense_hat, text_config)
        try:
            text_mode.update()  # Should not raise
        finally:
            text_mode.clear()


class TestLEDDisplayManager:
    """Tests for LEDDisplayManager."""

    @pytest.fixture
    def temp_config_path(self, tmp_path):
        """Create temporary config path."""
        return tmp_path / "led_config.json"

    def test_manager_init_mock(self, temp_config_path):
        """Test LED manager initialization with mock."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        assert manager.sense_hat is None
        assert manager.config is not None
        assert manager.running is False

    def test_manager_set_mode_off(self, temp_config_path):
        """Test setting LED mode to OFF."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        manager.set_mode(LEDMode.OFF)
        assert manager.current_mode is None
        assert manager.config.mode == LEDMode.OFF.value

    def test_manager_set_mode_worm(self, temp_config_path):
        """Test setting LED mode to WORM_ANIMATION."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        manager.set_mode(LEDMode.WORM_ANIMATION)
        assert isinstance(manager.current_mode, WormAnimationMode)
        assert manager.config.mode == LEDMode.WORM_ANIMATION.value

    def test_manager_set_mode_text(self, temp_config_path):
        """Test setting LED mode to TEXT_SCROLL."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        try:
            manager.set_mode(LEDMode.TEXT_SCROLL)
            assert isinstance(manager.current_mode, TextScrollMode)
            assert manager.config.mode == LEDMode.TEXT_SCROLL.value
        finally:
            manager.set_mode(LEDMode.OFF)  # Clean up

    def test_manager_mode_switching(self, temp_config_path):
        """Test switching between LED modes."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        try:
            # OFF -> WORM
            manager.set_mode(LEDMode.WORM_ANIMATION)
            assert isinstance(manager.current_mode, WormAnimationMode)

            # WORM -> TEXT
            manager.set_mode(LEDMode.TEXT_SCROLL)
            assert isinstance(manager.current_mode, TextScrollMode)

            # TEXT -> OFF
            manager.set_mode(LEDMode.OFF)
            assert manager.current_mode is None
        finally:
            manager.set_mode(LEDMode.OFF)  # Ensure cleanup

    def test_manager_start_stop(self, temp_config_path):
        """Test starting and stopping LED manager."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)

        # Start
        manager.start()
        assert manager.running is True
        assert manager.update_thread is not None

        # Stop
        manager.stop()
        assert manager.running is False

    def test_manager_ascii_preview_off(self, temp_config_path):
        """Test ASCII preview for OFF mode."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        preview = manager.get_ascii_preview()
        assert isinstance(preview, str)
        assert "·" in preview  # Empty grid

    def test_manager_ascii_preview_worm(self, temp_config_path):
        """Test ASCII preview for WORM mode."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        manager.set_mode(LEDMode.WORM_ANIMATION)
        preview = manager.get_ascii_preview()
        assert isinstance(preview, str)
        lines = preview.split("\n")
        assert len(lines) == 8

    def test_manager_save_config(self, temp_config_path):
        """Test saving LED configuration."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        manager.config.text = "Test Text"
        manager.save_config()

        assert temp_config_path.exists()
        with open(temp_config_path) as f:
            data = json.load(f)
            assert data["text"] == "Test Text"

    def test_manager_shutdown(self, temp_config_path):
        """Test LED manager shutdown."""
        manager = LEDDisplayManager(use_mock=True, config_path=temp_config_path)
        manager.start()
        manager.shutdown()

        assert manager.running is False
        assert temp_config_path.exists()  # Config saved


class TestEnums:
    """Tests for LED enums."""

    def test_led_mode_enum(self):
        """Test LEDMode enum values."""
        assert LEDMode.OFF.value == "off"
        assert LEDMode.TEXT_SCROLL.value == "text_scroll"
        assert LEDMode.WORM_ANIMATION.value == "worm_animation"

    def test_color_mode_enum(self):
        """Test ColorMode enum values."""
        assert ColorMode.SOLID.value == "solid"
        assert ColorMode.CUSTOM_RGB.value == "custom_rgb"
        assert ColorMode.RAINBOW.value == "rainbow"
        assert ColorMode.GRADIENT.value == "gradient"

    def test_scroll_speed_enum(self):
        """Test ScrollSpeed enum values."""
        assert ScrollSpeed.SLOW.value == 0.15
        assert ScrollSpeed.MEDIUM.value == 0.10
        assert ScrollSpeed.FAST.value == 0.05
