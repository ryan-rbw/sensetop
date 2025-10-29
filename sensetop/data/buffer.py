"""Circular buffer implementation for time-series data storage."""

from dataclasses import dataclass
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class BufferEntry(Generic[T]):
    """A single entry in the circular buffer."""

    timestamp: datetime
    value: T

    def __repr__(self) -> str:
        """String representation of buffer entry."""
        return f"BufferEntry(ts={self.timestamp.isoformat()}, value={self.value})"


class CircularBuffer(Generic[T]):
    """A fixed-size circular buffer for storing time-series data.

    When the buffer is full, new entries overwrite the oldest entries (FIFO).
    Provides O(1) append and read operations.
    """

    def __init__(self, capacity: int = 120) -> None:
        """Initialize circular buffer.

        Args:
            capacity: Maximum number of entries to store (default: 120).

        Raises:
            ValueError: If capacity is less than 1.
        """
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")

        self.capacity = capacity
        self._buffer: List[Optional[BufferEntry[T]]] = [None] * capacity
        self._head = 0  # Points to the next write position
        self._count = 0  # Number of entries currently in buffer

    def append(self, value: T, timestamp: Optional[datetime] = None) -> None:
        """Add an entry to the buffer.

        Args:
            value: The data value to store.
            timestamp: Timestamp for the entry. If None, uses current time.
        """
        if timestamp is None:
            timestamp = datetime.now()

        entry = BufferEntry(timestamp=timestamp, value=value)
        self._buffer[self._head] = entry

        # Move head to next position
        self._head = (self._head + 1) % self.capacity

        # Update count (cap at capacity)
        if self._count < self.capacity:
            self._count += 1

    def get_all(self) -> List[BufferEntry[T]]:
        """Get all entries in chronological order.

        Returns:
            List of all entries from oldest to newest.
        """
        if self._count == 0:
            return []

        result = []

        if self._count < self.capacity:
            # Buffer not yet full, entries are in order from index 0
            for i in range(self._count):
                entry = self._buffer[i]
                if entry is not None:
                    result.append(entry)
        else:
            # Buffer is full, wrap around from head
            for i in range(self.capacity):
                idx = (self._head + i) % self.capacity
                entry = self._buffer[idx]
                if entry is not None:
                    result.append(entry)

        return result

    def get_latest(self, count: int = 1) -> List[BufferEntry[T]]:
        """Get the N most recent entries.

        Args:
            count: Number of entries to retrieve.

        Returns:
            List of most recent entries (newest last).
        """
        if count < 1:
            return []

        all_entries = self.get_all()
        return all_entries[-count:] if all_entries else []

    def get_oldest(self, count: int = 1) -> List[BufferEntry[T]]:
        """Get the N oldest entries.

        Args:
            count: Number of entries to retrieve.

        Returns:
            List of oldest entries (oldest first).
        """
        if count < 1:
            return []

        all_entries = self.get_all()
        return all_entries[:count] if all_entries else []

    def clear(self) -> None:
        """Clear all entries from the buffer."""
        self._buffer = [None] * self.capacity
        self._head = 0
        self._count = 0

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self._count == 0

    def is_full(self) -> bool:
        """Check if buffer is at capacity."""
        return self._count == self.capacity

    def __len__(self) -> int:
        """Return number of entries currently in buffer."""
        return self._count

    def __repr__(self) -> str:
        """String representation of buffer."""
        return f"CircularBuffer(capacity={self.capacity}, count={self._count})"
