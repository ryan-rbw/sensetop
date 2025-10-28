"""Tests for application main entry point."""

import sys
from unittest.mock import Mock, patch

from sensetop.main import main


class TestMain:
    """Tests for main entry point."""

    def test_main_success(self):
        """Test main function runs successfully."""
        with patch("sensetop.main.SenseTopApp") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run = Mock()

            result = main()

            # Verify app was created and run
            mock_app_class.assert_called_once()
            mock_app.run.assert_called_once()
            mock_app.shutdown.assert_called_once()
            assert result == 0

    def test_main_keyboard_interrupt(self):
        """Test main function handles keyboard interrupt."""
        with patch("sensetop.main.SenseTopApp") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run.side_effect = KeyboardInterrupt()

            result = main()

            # KeyboardInterrupt should be handled gracefully
            mock_app.shutdown.assert_called_once()
            assert result == 130

    def test_main_general_exception(self):
        """Test main function handles general exceptions."""
        with patch("sensetop.main.SenseTopApp") as mock_app_class:
            mock_app_class.side_effect = Exception("Test error")

            result = main()

            assert result == 1

    def test_main_exception_during_shutdown(self):
        """Test main function handles exceptions during shutdown."""
        with patch("sensetop.main.SenseTopApp") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            mock_app.run = Mock()
            mock_app.shutdown.side_effect = Exception("Shutdown error")

            # Should still return 0 since app ran successfully
            result = main()

            assert result == 0
            mock_app.shutdown.assert_called_once()
