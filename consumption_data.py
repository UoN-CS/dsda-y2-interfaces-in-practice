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


class ConsumptionDataFile(ConsumptionData):
    """Access energy consumption data from a file.

    Consumption data file must be in a CSV file format with three columns and
    must include headers. The columns must contain:

        1. Consumption data in kWh.
        2. Start time in ISO 8601 format.
        3. End time in ISO 8601 format.

    Example of a valid consumption data file:

        Consumption (kWh), Start, End
        0.507, 2021-09-29T00:00:00+01:00, 2021-09-29T00:30:00+01:00
    """

    def __init__(self, filename: str, headers: list[str]):
        """Initialise the consumption data from file.

        Args:
            filename (str): Name of the CSV file to load data from.
        """
        pass

    def get_usage_for_range(self, start: int, end: int) -> int:
        return 0

    def has_usage_for_range(self, start: int, end: int) -> bool:
        return False
