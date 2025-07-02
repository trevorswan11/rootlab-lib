import serial
import matplotlib.pyplot as plt
import time
import os
from typing import List, Tuple
import random
import matplotlib.animation as animation
import statistics


class _MockSerial:
    """Simulates a basic serial.Serial interface."""

    def __init__(self, delay=0.1):
        self.delay = delay

    def readline(self):
        time.sleep(self.delay)
        return f"{random.uniform(0, 5):.3f}\n".encode()


def gather_data(
    port: str,
    name: str,
    baudrate: str = 9600,
    output_file_dir: str = "./data/Multilayer-Raw",
    output_image_dir: str = "./data/Multilayer-Series",
    output_image_ext: str = "png",
    mock: bool = False,
    relative: float = None,
    title: str = "Resistance vs. Time",
    time_unit: str = "s",
    resistance_unit: str = "Ohm",
    thresh: int = 1000,
) -> Tuple[List[float], List[float], str]:
    """
    Reads and plots serial data in real-time, and saves to a timestamped .txt file.

    Args:
        port (str): Serial port (e.g., 'COM3').
        name (str): Descriptive name used in output filename. You need not include the file extension
        baudrate (int, optional): Baud rate for serial communication. Defaults to '9600'
        output_file_dir (str, optional): Directory to save the output file. Defaults to '.', the current directory
        output_image_dir (str, optional): Directory to save the output image. Defaults to '.', the current directory
        output_image_dir (str, optional): Extension to use for the output image. You need not include the period. Defaults to 'png'
        mock (bool, optional): Indicates whether or not serial data should be simulated
        relative (float, optional): Indicates whether to plot read resistance or relative resistance (read / reference value). Defaults to None
        title (str): The title to use for the plot
        time_unit (str, optional): The unit to use for the x-axis. This will be formatted as "Time ({time_unit})". Defaults to "s"
        resistance_unit (str, optional): The unit to use for the y-axis. This will be formatted as "Resistance ({resistance_unit})". Defaults to "Ohm"
        thresh (int, optional): The number of readings gathered before the plot updates

    Returns:
        Tuple[List[float], List[float], List[float], List[float], str]: (R1_series, R2_series, R3_series, time_series, output_file_path)
    """
    ser = _MockSerial(0.1) if mock else serial.Serial(port=port, baudrate=baudrate)
    curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
    base_name = f"{curr_date}_{name}_{curr_time}"

    os.makedirs(output_file_dir, exist_ok=True)
    text_path = os.path.join(output_file_dir, f"{base_name}.txt")
    os.makedirs(output_image_dir, exist_ok=True)
    image_path = os.path.join(output_image_dir, f"{base_name}.{output_image_ext}")

    print(f"Recording to: {os.path.abspath(text_path)}")

    R1, R2, R3, t = [], [], [], []
    t0 = time.time()

    fig, ax = plt.subplots(figsize=(12, 9))
    # ax.set_ylim(1000, 50000)
    ax.set_xlabel(f"Time ({time_unit})")
    ax.set_ylabel(f"Resistance ({resistance_unit})")
    ax.set_title(title)
    ax.grid(True)

    (line1,) = ax.plot([], [], label="Bottom")
    (line2,) = ax.plot([], [], label="Middle")
    (line3,) = ax.plot([], [], label="Top")
    ax.legend()

    f = open(text_path, "w")

    def update(frame):
        try:
            raw = ser.readline().decode().strip().split(",")
            if len(raw) != 3:
                return

            r1, r2, r3 = float(raw[0]), float(raw[1]), float(raw[2])
            timestamp = time.time() - t0

            R1.append(r1)
            R2.append(r2)
            R3.append(r3)
            t.append(timestamp)

            f.write(f"{r1},{r2},{r3},{timestamp:.3f}\n")
            f.flush()

            # Limit to max_points
            R1_trim = R1[-thresh:]
            R2_trim = R2[-thresh:]
            R3_trim = R3[-thresh:]
            t_trim = t[-thresh:]

            # Bring values into reference resistance range
            if relative is not None:
                R1_trim = [res1 / relative for res1 in R1_trim]
                R2_trim = [res2 / relative for res2 in R2_trim]
                R3_trim = [res3 / relative for res3 in R3_trim]

            line1.set_data(t_trim, R1_trim)
            line2.set_data(t_trim, R2_trim)
            line3.set_data(t_trim, R3_trim)

            ax.relim()
            ax.autoscale_view()
        except Exception as e:
            print(f"Error in update: {e}")

    ani = animation.FuncAnimation(fig, update, interval=50, cache_frame_data=False)
    plt.tight_layout()

    try:
        plt.show()
    except KeyboardInterrupt:
        print("Interrupted by user.")

    print("Closing...")
    f.close()
    fig.savefig(image_path)
    print(f"Plot saved to {image_path}")
    return R1, R2, R3, t, text_path


def plot(
    file: str,
    output_file: str,
    title: str,
    time_unit: str = "s",
    resistance_unit: str = "Ohm",
    output_file_extension: str = "png",
) -> None:
    """Creates a plot of the voltage data against time. Overwrites any plot or file of the same name. Only use for recovery.

    Args:
        file (str): The file with raw data formatted as {r1},{r2},{r3},{time}, where r1 is the top and r3 is the bottom
        output_file (str): The output file to save the plot to. You need not specify the file extension
        title (str): The title to use for the plot
        time_unit (str, optional): The unit to use for the x-axis. This will be formatted as "Time ({time_unit})". Defaults to "s"
        resistance_unit (str, optional): The unit to use for the y-axis. This will be formatted as "Resistance ({resistance_unit})". Defaults to "Ohm"
        output_file_extension (str, optional): The file extension to use with the output file. Do not include the period. Defaults to "png"

    """
    # Prepare series
    time_data = []
    resistance_top = []
    resistance_middle = []
    resistance_bottom = []

    with open(file, "r") as f:
        for line in f.readlines():
            parts = line.strip().split(",")
            if len(parts) != 4:
                continue  # Skip malformed lines
            try:
                r1, r2, r3, t = map(float, parts)
                resistance_top.append(r1)
                resistance_middle.append(r2)
                resistance_bottom.append(r3)
                time_data.append(t)
            except ValueError:
                continue  # Skip lines that fail to parse

    # Plot the data
    plt.figure(figsize=(12, 9))
    plt.plot(time_data, resistance_top, label="Top", color="red")
    plt.plot(time_data, resistance_middle, label="Middle", color="green")
    plt.plot(time_data, resistance_bottom, label="Bottom", color="blue")

    plt.title(title, fontsize=25)
    plt.grid(True)
    plt.xlabel(f"Time ({time_unit})", fontsize=25)
    plt.ylabel(f"Resistance ({resistance_unit})", fontsize=25)
    plt.tick_params(labelsize=20)
    plt.legend(fontsize=20)
    plt.tight_layout()

    full_output_path = f"{output_file}_SERIES.{output_file_extension}"
    print(f"Saving {os.path.abspath(full_output_path)}")
    print(f"\tCurrent File: {os.path.basename(full_output_path)}")
    plt.savefig(full_output_path)
    plt.show()


def analyze(
    file: str,
    output_file: str,
) -> List[Tuple[float]]:
    """Reads the resistance data from the file and writes statistics about each channel to the output file

    Args:
        file (str): The file with raw data formatted as {r1},{r2},{r3},{time}, where r1 is the top and r3 is the bottom. The time slot is not read and is hence optional
        output_file (str): The output file to save the data to

    Returns:
        List[Tuple[float]]: (mean, median, std, minim, maxim) for each layer, where List[0] is layer 1 and List[2] is layer 3
    """
    resistance_top = []
    resistance_middle = []
    resistance_bottom = []

    with open(file, "r") as f:
        for line in f.readlines():
            parts = line.strip().split(",")
            if len(parts) != 3 and len(parts) != 4:
                continue  # Skip malformed lines
            try:
                r1 = float(parts[0])
                r2 = float(parts[1])
                r3 = float(parts[2])
                resistance_top.append(r1)
                resistance_middle.append(r2)
                resistance_bottom.append(r3)
            except ValueError:
                continue  # Skip lines that fail to parse

    with open(output_file, "w") as f:
        res = [resistance_top, resistance_middle, resistance_bottom]
        names = ["Top Resistor", "Middle Resistor", "Bottom Resistor"]

        results = []

        for r, n in zip(res, names):
            f.write(f"{n}\n")
            mean = statistics.mean(r)
            median = statistics.median(r)
            std = "NaN"
            try:
                statistics.stdev(r)
            except:
                std = "NaN"
            minim = min(r)
            maxim = max(r)
            f.write(
                f"  {mean = }\n  {median = }\n  {std = }\n  {minim = }\n  {maxim = }\n\n"
            )
            results.append((mean, median, std, minim, maxim))

            print(f"{n}")
            print(
                f"  {mean = }\n  {median = }\n  {std = }\n  {minim = }\n  {maxim = }\n"
            )


if __name__ == "__main__":
    out_dir = "../../test_files/"
    file = "../../test_files/25-07-01_Resistance-INITIAL_15-21-19.txt"

    plot(file, out_dir + "what", "Test")
    analyze(file, out_dir + "who.txt")
