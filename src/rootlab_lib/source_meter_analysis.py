"""The main way to interact with data outputted by the source meter in lab."""

import pandas as pd
from typing import Tuple, List
import time as t
import os
import csv
import matplotlib.pyplot as plt


def voltage_readings_to_resistance(
    input_filepath: str,
    amperage: float,
    output_dir: str | None,
) -> str:
    """Converts the voltage data in a file to resistance data based on the given amperage and writes it out to a file of a similar name.

    Args:
        input_filepath (str): The filepath of the original file with the 
        amperage (float): The amperage set with the SourceMeter. This should be a unit consistent with the given data
        output_dir (str | None): The directory to store the output file. If this is None, then the directory of the input is preserved

    Returns:
        str: The filepath of the output file
    """
    if not os.path.isfile(input_filepath):
        raise FileNotFoundError(f"Input file not found: {input_filepath}")

    if amperage == 0:
        raise ValueError("Amperage cannot be zero when calculating resistance.")

    # Set output directory to input's dir if not provided
    if output_dir is None:
        output_dir = os.path.dirname(input_filepath)
    os.makedirs(output_dir, exist_ok=True)

    # Parse CSV and isolate voltage + time data
    two_col_rows = []
    rest_rows = []
    switch_found = False

    with open(input_filepath, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not switch_found and len(row) == 2:
                two_col_rows.append(row)
            else:
                switch_found = True
                rest_rows.append(row)

    headers = rest_rows[0]
    df = pd.DataFrame(rest_rows[1:], columns=headers)

    voltage_col = "Reading"
    time_col = "Relative Time"

    df[voltage_col] = pd.to_numeric(df[voltage_col], errors="coerce")
    df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
    df.dropna(subset=[voltage_col, time_col], inplace=True)

    df["Resistance"] = df[voltage_col] / amperage

    # Create output .txt file with format time,resistance
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    base = os.path.basename(input_filepath).rsplit(".", 1)[0]
    output_filename = f"{curr_date}_{base}_resistance_{curr_time}.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w") as out:
        for _, row in df.iterrows():
            out.write(f"{row[time_col]},{row['Resistance']}\n")

    return output_path

def _extract_time_resistance_data(filepath: str) -> Tuple[List[float], List[float]]:
    """Extracts time and resistance data from a text file formatted as 'time,resistance' on each line.

    Args:
        filepath (str): Path to the formatted data file

    Returns:
        Tuple[List[float], List[float]]: Lists of time values and resistance values
    """
    time_vals = []
    resistance_vals = []

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    with open(filepath, "r") as f:
        for line in f:
            try:
                t_str, r_str = line.strip().split(",")
                time_vals.append(float(t_str))
                resistance_vals.append(float(r_str))
            except ValueError:
                continue  # skip malformed lines

    return time_vals, resistance_vals

def analyze(
    input_filepath: str,
    output_name: str,
    output_dir: str = ".",
    output_image_ext: str = "png",
    title: str = "Source Meter Readings",
    readings_unit: str = "Ohms",
    time_unit: str = "seconds",
    write_out: bool = False,
    log_scale: bool = False,
) -> Tuple[List[float], List[float], str]:
    """
    Writes and plots source meter resistance readings vs time and saves a .png of the data.

    Args:
        input_filepath (str): The name of the input file with the data to be read. This should be a csv file.
        output_name (str): Descriptive name used in output filename. The current date and time will be combined with this. Do not include the extension or path
        output_dir (str, optional): The path to be used for the output image. Defaults to '.', the current directory
        output_image_ext (str, optional): The image extension to be used for the output image. You need not include the period. Defaults to 'png'
        title (str, optional): The title of the plot. Defaults to 'Source Meter Readings'
        readings_unit (str, optional): The unit of the readings outputted. Defaults to 'Ohms'
        time_unit (str, optional): The unit of the time values reported. Defaults to seconds
        write_out (bool, optional): Determines whether or not to write the (time, resistance) data out to a file. Defaults to false
        log_scale (bool, optional): If True, plots the readings on a logarithmic y-axis. Defaults to False
    Returns:
        Tuple(List[float], List[float], str): (time_series, resistance_series, data_filepath_out) where data_filepath_out is a txt file of [time, data]
    """
    if not os.path.isfile(input_filepath):
        print("Error: Input filepath is not a valid file")
        return

    os.makedirs(output_dir, exist_ok=True)
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    output_img = f"{curr_date}_{output_name}_{curr_time}.{output_image_ext}"
    output_img_path = os.path.join(output_dir, output_img)

    output_data = f"{curr_date}_{output_name}_{curr_time}.txt"
    output_data_path = os.path.join(output_dir, output_data)

    try:
        time_series, resistance_series = _extract_time_resistance_data(input_filepath)

        if len(time_series) != len(resistance_series):
            raise ValueError("Time and resistance series are not the same length.")

        if write_out:
            with open(output_data_path, "w") as f:
                for i in range(len(time_series)):
                    f.write(f"{time_series[i]},{resistance_series[i]}\n")
            print(f"Saving {os.path.abspath(output_data_path)}")

        plt.figure(figsize=(10, 6))
        plt.plot(time_series, resistance_series, linestyle="-", color="blue")
        plt.title(title)
        plt.xlabel(f"Time ({time_unit})")
        plt.ylabel(f"Readings ({readings_unit})")
        plt.grid(True)
        
        if log_scale:
            plt.yscale('log')
            
        plt.tight_layout()
        plt.savefig(output_img_path)
        print(f"Saving {os.path.abspath(output_img_path)}")
        print(f"\tCurrent File: {os.path.basename(output_img_path)}")
        plt.show()

        return (time_series, resistance_series, output_data_path)

    except Exception as e:
        print(f"Fatal error analyzing data: {e}")
        return
    
def analyze_concat(
    input_filepaths: List[str],
    output_name: str,
    output_dir: str = ".",
    output_image_ext: str = "png",
    title: str = "Concatenated Source Meter Readings",
    readings_unit: str = "Ohms",
    time_unit: str = "seconds",
    write_out: bool = False,
    log_scale: bool = False,
) -> Tuple[List[float], List[float], str]:
    """
    Reads and appends resistance vs time data from multiple files, resets time to start at 0, and plots it as one continuous curve.
    Each dataset is shifted linearly in time to maintain continuity across concatenation.

    Args:
        input_filepaths (List[str]): List of filepaths to txt files, each formatted as 'time,resistance' on each line
        output_name (str): Descriptive name used in the output filename. The current date and time will be combined with this
        output_dir (str, optional): Directory for output image and optionally data file. Defaults to current directory
        output_image_ext (str, optional): Image format extension (e.g. 'png', 'svg'). Defaults to 'png'
        title (str, optional): Title of the plot. Defaults to 'Concatenated Source Meter Readings'
        readings_unit (str, optional): Y-axis unit label. Defaults to 'Ohms'
        time_unit (str, optional): X-axis unit label. Defaults to 'seconds'
        write_out (bool, optional): If True, saves concatenated time/resistance data to a .txt file. Defaults to False
        log_scale (bool, optional): If True, uses logarithmic scale for Y-axis. Defaults to False

    Returns:
        Tuple[List[float], List[float], str]: (concatenated_time_series, concatenated_resistance_series, data_filepath_out)
    """
    all_times = []
    all_resistances = []
    time_offset = 0.0

    os.makedirs(output_dir, exist_ok=True)
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    output_img = f"{curr_date}_{output_name}_{curr_time}.{output_image_ext}"
    output_img_path = os.path.join(output_dir, output_img)

    output_data = f"{curr_date}_{output_name}_{curr_time}.txt"
    output_data_path = os.path.join(output_dir, output_data)

    for i, filepath in enumerate(input_filepaths):
        try:
            times, resistances = _extract_time_resistance_data(filepath)

            if len(times) != len(resistances):
                print(f"Warning: Skipping file due to mismatch in length — {filepath}")
                continue

            # Normalize time to start from 0 and shift by offset
            if times:
                times = [t + time_offset for t in times]
                time_offset = times[-1] + (times[1] - times[0] if len(times) > 1 else 1.0)  # maintain step

            all_times.extend(times)
            all_resistances.extend(resistances)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue

    if write_out:
        with open(output_data_path, "w") as f:
            for t_val, r_val in zip(all_times, all_resistances):
                f.write(f"{t_val},{r_val}\n")
        print(f"Saving concatenated data: {os.path.abspath(output_data_path)}")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(all_times, all_resistances, linestyle="-", color="green")
    plt.title(title)
    plt.xlabel(f"Time ({time_unit})")
    plt.ylabel(f"Readings ({readings_unit})")
    plt.grid(True)

    if log_scale:
        plt.yscale("log")

    plt.tight_layout()
    plt.savefig(output_img_path)
    print(f"Saving plot: {os.path.abspath(output_img_path)}")
    print(f"\tCurrent File: {os.path.basename(output_img_path)}")
    plt.show()

    return all_times, all_resistances, output_data_path if write_out else ""
