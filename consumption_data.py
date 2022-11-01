from abc import ABC, abstractmethod
from datetime import datetime
from inspect import cleandoc
from typing import Final
from unittest import mock

import pandas as pd
import pytest
from pytz import utc

UNIX_EPOCH: Final[datetime] = datetime(year=1970, month=1, day=1, tzinfo=utc)


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
    must include headers. Columns must be delimited with a comma and space (",
    ") and must contain:

        1. Consumption data in kWh.
        2. Start time in ISO 8601 format.
        3. End time in ISO 8601 format.

    Example of a valid consumption data file:

        Consumption (kWh), Start, End
        0.507, 2021-09-29T00:00:00+01:00, 2021-09-29T00:30:00+01:00
    """

    # columns in the internal dataframe
    COL_USAGE: Final[str] = "Consumption (kWh)"
    COL_START: Final[str] = "Start"
    COL_END: Final[str] = "End"

    def __init__(self, filename: str) -> None:
        """Initialise the consumption data from file.

        Args:
            filename (str): Name of the CSV file to load data from.
        """
        # read csv using pandas
        self._df: pd.DataFrame = pd.read_csv(
            filename, header=0, delimiter=", ", engine="python"
        )
        # convert kWh to Wh
        self._df[ConsumptionDataFile.COL_USAGE] *= 1000
        # convert times to unix timestamps with milliseconds
        self._col_iso_to_unix(ConsumptionDataFile.COL_START)
        self._col_iso_to_unix(ConsumptionDataFile.COL_END)
        # make all columns int
        self._df = self._df.astype(int)

    def _col_iso_to_unix(self, col: str) -> None:
        """Convert an ISO 8601 column in the data to be Unix timestamps.

        Args:
            col (str): Column name.
        """
        self._df[col] = self._df[col].apply(
            lambda x: (datetime.fromisoformat(x) - UNIX_EPOCH).total_seconds()
        )

    def get_usage_for_range(self, start: int, end: int) -> int:
        if self.has_usage_for_range(start, end):
            return self._df[
                (self._df[ConsumptionDataFile.COL_START] >= start)
                & (self._df[ConsumptionDataFile.COL_END] <= end)
            ][ConsumptionDataFile.COL_USAGE].sum()
        else:
            raise ConsumptionDataException(
                f"Attempting to get usage for invalid range: {start!r} to"
                f" {end!r}."
            )

    def has_usage_for_range(self, start: int, end: int) -> bool:
        # validate the times exist
        if start not in self._df[ConsumptionDataFile.COL_START].values:
            raise ConsumptionDataException(
                f"Start time {start!r} not found in data."
            )
        elif end not in self._df[ConsumptionDataFile.COL_END].values:
            raise ConsumptionDataException(
                f"End time {end!r} not found in data."
            )
        # extract data within the time range
        df = self._df[
            (self._df[ConsumptionDataFile.COL_START] >= start)
            & (self._df[ConsumptionDataFile.COL_END] <= end)
        ].copy()
        # check that the extracted data is continuous and non-empty
        df["Continuous"] = df[ConsumptionDataFile.COL_END] == df[
            ConsumptionDataFile.COL_START
        ].shift(-1)
        if df["Continuous"].empty:
            raise Exception(
                f"No data matches range, check range is valid: {start!r} to"
                f" {end!r}."
            )
        # set last entry to True - when shifting will be NaN
        df.iat[-1, df.columns.get_loc("Continuous")] = True
        return df[~df["Continuous"]].empty


def test_consumption_data_file_get_usage_for_range():
    # load the mocked data
    mock_open = mock.mock_open(
        read_data=cleandoc(
            """Consumption (kWh), Start, End
            0.0, 2000-01-01T00:00:00+00:00, 2000-01-02T00:00:00+00:00
            1.0, 2000-01-08T00:00:00+00:00, 2000-01-09T00:00:00+00:00
            2.0, 2000-01-15T00:00:00+00:00, 2000-01-16T00:00:00+00:00
            3.0, 2000-01-22T00:00:00+00:00, 2000-01-23T00:00:00+00:00
            4.0, 2000-01-23T00:00:00+00:00, 2000-01-24T00:00:00+00:00"""
        )
    )
    cdf: ConsumptionDataFile
    with mock.patch("builtins.open", mock_open):
        cdf = ConsumptionDataFile(filename="filename")

    # check that invalid ranges correctly raise exceptions
    invalid = [
        # range doesn't have any data
        (
            int(
                datetime.fromisoformat("2000-01-12T00:00:00+00:00").timestamp()
            ),
            int(
                datetime.fromisoformat("2000-01-14T00:00:00+00:00").timestamp()
            ),
        ),
        # range includes only partial data
        (
            int(
                datetime.fromisoformat("2000-01-15T00:00:00+00:00").timestamp()
            ),
            int(
                datetime.fromisoformat("2000-01-23T00:00:00+00:00").timestamp()
            ),
        ),
    ]
    for start, end in invalid:
        with pytest.raises(ConsumptionDataException):
            datetime.fromisoformat("2000-01-08T00:00:00+00:00").timestamp()
            cdf.get_usage_for_range(start=start, end=end)

    # test with valid ranges
    valid = [
        # single entry
        (
            int(
                datetime.fromisoformat("2000-01-01T00:00:00+00:00").timestamp()
            ),
            int(
                datetime.fromisoformat("2000-01-02T00:00:00+00:00").timestamp()
            ),
            0,
        ),
        # multiple entries
        (
            int(
                datetime.fromisoformat("2000-01-22T00:00:00+00:00").timestamp()
            ),
            int(
                datetime.fromisoformat("2000-01-24T00:00:00+00:00").timestamp()
            ),
            7000,
        ),
    ]
    for start, end, total in valid:
        assert cdf.get_usage_for_range(start=start, end=end) == total
