"""The main way to interact with data outputted by the source meter in lab."""

import pandas as pd
from typing import Tuple, List
import os
import csv
import matplotlib.pyplot as plt


def gather_data(
    input_filepath: str,
    output_filepath: str,
    reading_column_name: str = "Reading",
    time_column_name: str = "Relative Time",
    title: str = "Source Meter Readings",
    readings_unit: str = "Ohms",
    time_unit: str = "seconds",
    offset: float = 0,
) -> Tuple[List[float], List[float]]:
    """
    Writes and plots source meter resistance readings vs time and saves a .png of the data.

    Args:
        input_filepath (str): The name of the input file with the data to be read. This should be a csv file.
        output_filepath (str): Descriptive name used in output filename. This should be a .png file
        reading_column_name (str, optional): The name of the column in the data that holds the readings. Defaults to 'Reading'
        time_column_name (str, optional): The name of the column in the data that holds the time values. Defaults to 'Relative Time'
        title (str, optional): The title of the plot. Defaults to 'Source Meter Readings'
        readings_unit (str, optional): The unit of the readings outputted. Defaults to 'Ohms'
        time_unit (str, optional): The unit of the time values reported. Defaults to seconds
        offset (float, optional): The offset to add to the readings to account for the source meters data truncation for repetitive values. Defaults to 0
    Returns:
        Tuple(List[float], List[float]): (time_series, resistance_series)
    """
    # Prep the file system for reading and writing
    if not os.path.isfile(input_filepath):
        print("Error: Input filepath is not a valid file")
        return

    output_directory = os.path.dirname(output_filepath)
    os.makedirs(output_directory, exist_ok=True)

    # Initialize the row vectors to hold the differently sized data
    two_col_rows = []
    rest_rows = []
    switch_found = False

    # open the csv file and read in the data until the row length changes
    with open(input_filepath, "r", newline="") as f:
        try:
            reader = csv.reader(f)
            for row in reader:
                if not switch_found and len(row) == 2:
                    two_col_rows.append(row)
                else:
                    switch_found = True
                    rest_rows.append(row)

            # Create pandas dataframes out of the two vectors for processing
            headers_2col = two_col_rows[0]
            headers_21col = rest_rows[0]

            df1 = pd.DataFrame(
                two_col_rows[1:], columns=headers_2col
            )  # df1 has the first part of the data, which we can omit for now
            df2 = pd.DataFrame(
                rest_rows[1:], columns=headers_21col
            )  # df2 contains the usable data, but all we need is the readings and times

            # Convert to numeric, with error coercion
            df2[reading_column_name] = pd.to_numeric(
                df2[reading_column_name], errors="coerce"
            )
            df2[time_column_name] = pd.to_numeric(
                df2[time_column_name], errors="coerce"
            )

            # Drop rows with NaN values in the columns we care about
            df2.dropna(subset=[reading_column_name, time_column_name], inplace=True)

            # Extract lists and apply offset
            readings = (df2[reading_column_name] + offset).tolist()
            time = df2[time_column_name].tolist()

            plt.figure(figsize=(10, 6))
            plt.plot(time, readings, linestyle="-", color="blue")
            plt.title(title)
            plt.xlabel(f"Time ({time_unit})")
            plt.ylabel(f"Readings ({readings_unit})")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(output_filepath)
            print(f"Saving {os.path.abspath(output_filepath)}")
            print(f"\tCurrent File: {os.path.basename(output_filepath)}")
            plt.show()

            return (time, readings)

        except Exception as e:
            print(f"Fatal error reading input csv file: {e}")
            return
