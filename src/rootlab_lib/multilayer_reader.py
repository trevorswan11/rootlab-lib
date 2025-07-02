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
        return f"{random.uniform(4000, 50000):.3f},{random.uniform(4000, 50000):.3f},{random.uniform(4000, 50000):.3f}\n".encode()


def gather_data(
    port: str,
    name: str,
    baudrate: str = 9600,
    output_file_dir: str = "./data/Multilayer-Raw",
    output_image_dir: str = "./data/Multilayer-Series",
    output_image_ext: str = "png",
    mock: bool = False,
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
        thresh (int, optional): The number of readings gathered before the plot updates

    Returns:
        Tuple(List[float], List[float], List[float], List[float], str): (R1_series, R2_series, R3_series, time_series, output_file_path)
    """
    ser = _MockSerial(0.001) if mock else serial.Serial(port=port, baudrate=baudrate)
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

            line1.set_data(t_trim, R1_trim)
            line2.set_data(t_trim, R2_trim)
            line3.set_data(t_trim, R3_trim)

            y_max = max(max(R1_trim, default=0), max(R2_trim, default=0), max(R3_trim, default=0))
            ax.set_ylim(0, y_max * 1.1 if y_max > 0 else 1)
        except Exception as e:
            print(f"Error in update: {e}")

    ani = animation.FuncAnimation(fig, update, interval=50, cache_frame_data=False, blit=False)
    plt.tight_layout()

    try:
        plt.show()
    except KeyboardInterrupt:
        print("Interrupted by user.")

    print("Closing...")
    f.close()
    fig.savefig(image_path)
    print(f"Plot saved to {image_path}")
    return R1, R2, R3, t, ani, text_path