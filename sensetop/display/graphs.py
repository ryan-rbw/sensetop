"""Graph visualization using ASCII and Unicode characters."""

from typing import List, Optional, Tuple


class GraphRenderer:
    """Render time-series data as ASCII/Unicode graphs."""

    # Unicode sparkline characters for vertical graph
    SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"

    # ASCII characters for bar chart
    ASCII_BLOCK_CHARS = "▁▂▃▄▅▆▇█"

    @staticmethod
    def render_sparkline(
        values: List[float],
        width: int = 20,
    ) -> str:
        """Render a sparkline (mini graph) for a series of values.

        Args:
            values: List of numeric values to graph.
            width: Maximum width in characters.

        Returns:
            Sparkline string using Unicode characters.
        """
        if not values:
            return ""

        if len(values) > width:
            # Downsample to fit width
            step = len(values) / width
            sampled = [values[int(i * step)] for i in range(width)]
        else:
            sampled = values

        min_val = min(sampled)
        max_val = max(sampled)
        range_val = max_val - min_val

        if range_val == 0:
            # All values are the same
            return GraphRenderer.SPARKLINE_CHARS[4] * len(sampled)

        # Normalize values to 0-7 range (8 chars in sparkline)
        normalized = [int((v - min_val) / range_val * 7) for v in sampled]

        # Map to sparkline characters
        sparkline = "".join(GraphRenderer.SPARKLINE_CHARS[i] for i in normalized)

        return sparkline

    @staticmethod
    def render_bar_chart(
        values: List[float],
        height: int = 5,
        width: int = 30,
    ) -> str:
        """Render a bar chart using ASCII characters.

        Args:
            values: List of numeric values to graph.
            height: Height of the chart in lines.
            width: Width of the chart in characters.

        Returns:
            Multi-line ASCII bar chart.
        """
        if not values or height < 1 or width < 1:
            return ""

        # Downsample values to fit width
        if len(values) > width:
            step = len(values) / width
            sampled = [values[int(i * step)] for i in range(width)]
        else:
            sampled = values

        min_val = min(sampled)
        max_val = max(sampled)
        range_val = max_val - min_val

        if range_val == 0:
            # All values are the same
            normalized = [5] * len(sampled)  # Middle height
        else:
            # Normalize to 0-(height*8) range
            max_normalized = height * 8
            normalized = [int((v - min_val) / range_val * max_normalized) for v in sampled]

        # Build chart from top to bottom
        lines = []
        for h in range(height * 8 - 1, -1, -8):
            line = ""
            for val in normalized:
                if val > h + 8:
                    line += "█"
                elif val > h:
                    char_idx = val - h
                    line += GraphRenderer.ASCII_BLOCK_CHARS[char_idx - 1]
                else:
                    line += " "
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def render_line_graph(
        values: List[float],
        height: int = 8,
        width: int = 40,
    ) -> str:
        """Render a line graph using ASCII characters.

        Args:
            values: List of numeric values to graph.
            height: Height of the graph in lines.
            width: Width of the graph in characters.

        Returns:
            Multi-line ASCII line graph.
        """
        if not values or height < 1 or width < 1:
            return ""

        # Downsample values to fit width
        if len(values) > width:
            step = len(values) / width
            sampled = [values[int(i * step)] for i in range(width)]
        else:
            sampled = values

        min_val = min(sampled)
        max_val = max(sampled)
        range_val = max_val - min_val

        if range_val == 0:
            # All values are the same - draw middle line
            lines = []
            mid = height // 2
            for h in range(height):
                if h == mid:
                    lines.append("-" * width)
                else:
                    lines.append("|" + " " * (width - 2) + "|")
            return "\n".join(lines)

        # Normalize values to (height-1) range
        normalized = [int((v - min_val) / range_val * (height - 1)) for v in sampled]

        # Create graph grid
        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Place points and connect with lines
        for i, normalized_val in enumerate(normalized):
            row = height - 1 - normalized_val
            grid[row][i] = "●"

        # Connect consecutive points with lines
        for i in range(len(normalized) - 1):
            y1 = height - 1 - normalized[i]
            y2 = height - 1 - normalized[i + 1]

            if abs(y1 - y2) <= 1:
                # Simple horizontal or diagonal connection
                if y1 != y2:
                    row = min(y1, y2)
                    grid[row][i + 1] = "·"
            else:
                # Vertical or steep diagonal
                step = 1 if y2 > y1 else -1
                for y in range(y1, y2, step):
                    grid[y][i + 1] = "·"

        # Add borders and convert to string
        lines = []
        for row in grid:
            lines.append("|" + "".join(row) + "|")

        return "\n".join(lines)

    @staticmethod
    def render_mini_graph(
        values: List[float],
        mode: str = "sparkline",
        height: int = 3,
        width: int = 15,
    ) -> str:
        """Render a small inline graph for display in tables.

        Args:
            values: List of numeric values to graph.
            mode: 'sparkline', 'bar', or 'line'.
            height: Height for bar/line graphs.
            width: Width in characters.

        Returns:
            Single-line or small multi-line graph.
        """
        if mode == "bar":
            return GraphRenderer.render_bar_chart(values, height, width)
        elif mode == "line":
            return GraphRenderer.render_line_graph(values, height, width)
        else:  # sparkline (default)
            return GraphRenderer.render_sparkline(values, width)

    @staticmethod
    def format_value_with_range(
        value: float,
        min_val: float,
        max_val: float,
        format_str: str = ".2f",
    ) -> Tuple[str, str]:
        """Format a value with color indicator based on range position.

        Args:
            value: The value to format.
            min_val: Minimum value in range.
            max_val: Maximum value in range.
            format_str: Python format string for the value.

        Returns:
            Tuple of (formatted_value, position_indicator).
            Indicator: "◄" at min, "■" in middle, "►" at max.
        """
        formatted = f"{value:{format_str}}"

        range_val = max_val - min_val
        if range_val == 0:
            position = "■"
        else:
            ratio = (value - min_val) / range_val
            if ratio < 0.33:
                position = "◄"
            elif ratio > 0.67:
                position = "►"
            else:
                position = "■"

        return (formatted, position)


def create_trend_indicator(trend: str) -> str:
    """Create a visual trend indicator.

    Args:
        trend: Trend string ("↑", "→", "↓", or "?").

    Returns:
        Formatted trend indicator.
    """
    indicators = {
        "↑": " ↑ ",  # Rising
        "→": " → ",  # Flat
        "↓": " ↓ ",  # Falling
        "?": " ? ",  # Unknown
    }
    return indicators.get(trend, " ? ")
