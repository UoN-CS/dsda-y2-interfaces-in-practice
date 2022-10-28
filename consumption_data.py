from abc import ABC, abstractmethod


class ConsumptionDataException(Exception):
    """Exception for consumption data related issues."""

    pass


class ConsumptionData(ABC):
    """Abstract class for fetching energy consumption data."""

    @abstractmethod
    def get_usage_for_range(self, start: int, end: int) -> int:
        """Get the total usage data for a given time range in Watt hours.

        Start time is inclusive and end time is exclusive, i.e. [start, end).

        Args:
            start (int): Start time of range as a UNIX timestamp (inclusive).
            end (int): End time of range as a UNIX timestamp (exclusive).

        Raises:
            ConsumptionDataException: If the range is invalid or the data is
                incomplete.

        Returns:
            int: Total usage data for the range in Watt hours (Wh).
        """
        pass

    @abstractmethod
    def has_usage_for_range(self, start: int, end: int) -> bool:
        """Check if usage data exists for the complete range specified.

        Args:
            start (int): _description_
            end (int): _description_

        Returns:
            bool: True only if data exists for the whole range, else False.
        """
        pass
