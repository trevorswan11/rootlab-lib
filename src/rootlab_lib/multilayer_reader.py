import serial
import matplotlib.pyplot as plt
import time
import os
from typing import List, Tuple
import random
import matplotlib.animation as animation

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
    reference: float = None,
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
        thresh (int, optional): The number of readings gathered before the plot updates

    Returns:
        Tuple(List[float], List[float], List[float], List[float], str): (R1_series, R2_series, R3_series, time_series, output_file_path)
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
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Resistance (Ohm)")
    ax.set_title("Resistance vs. Time")
    ax.grid(True)

    line1, = ax.plot([], [], label="Bottom")
    line2, = ax.plot([], [], label="Middle")
    line3, = ax.plot([], [], label="Top")
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
            if reference is not None:
                R1_trim = [res1 / reference for res1 in R1_trim] 
                R2_trim = [res2 / reference for res2 in R2_trim] 
                R3_trim = [res3 / reference for res3 in R3_trim] 

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
    output_file_extension: str = "png",
) -> None:
    """Creates a plot of the voltage data against time. Overwrites any plot or file of the same name. Only use for recovery.

    Args:
        file (str): The file with raw data formatted as {r1},{r2},{r3},{time}, where r1 is the top and r3 is the bottom
        output_file (str): The output file to save the plot to. You need not specify the file extension
        title (str): The title to use for the plot
        output_file_extension (str, optional): The file extension to use with the output file. Do not include the period. Defaults to "png"

    Returns:
        List[float]: The list of the extracted average values from each plateau
    """
    # Prepare series
    time_data = []
    resistance_top = []
    resistance_middle = []
    resistance_bottom = []

    with open(file, 'r') as f:
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
    plt.xlabel("Time (s)", fontsize=25)
    plt.ylabel("Resistance (Ohm)", fontsize=25)
    plt.tick_params(labelsize=20)
    plt.legend(fontsize=20)
    plt.tight_layout()

    full_output_path = f"{output_file}_SERIES.{output_file_extension}"
    print(f"Saving {os.path.abspath(full_output_path)}")
    print(f"\tCurrent File: {os.path.basename(full_output_path)}")
    plt.savefig(full_output_path)
    plt.show()


if __name__ == "__main__":
    out_dir = "../../test_files/"
    file = gather_data(
        "COM3", "test", output_file_dir=out_dir, output_image_dir=out_dir
    )[-1]
    
    plot(file, out_dir+"what", "Test")
