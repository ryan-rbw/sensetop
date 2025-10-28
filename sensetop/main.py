"""Main entry point for SenseTop application."""

import asyncio
import sys
from typing import Optional

from sensetop.app import SenseTopApp


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    app: Optional[SenseTopApp] = None
    try:
        # Create and run the application
        app = SenseTopApp()
        app.run()
        return 0

    except KeyboardInterrupt:
        print("\nApplication interrupted by user.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    finally:
        # Ensure proper cleanup
        if app is not None:
            try:
                app.shutdown()
            except Exception as e:
                print(f"Error during shutdown: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
