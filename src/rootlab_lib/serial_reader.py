"""The main way to interact with data outputted by the arduino in lab."""

import serial
import matplotlib.pyplot as plt
import time
import os
from typing import List, Tuple
import random


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
    output_dir: str = ".",
    mock: bool = False,
    thresh: int = 40,
) -> Tuple[List[float], List[float]]:
    """
    Reads and plots serial data in real-time, and saves to a timestamped .txt file.

    Args:
        port (str): Serial port (e.g., 'COM3').
        name (str): Descriptive name used in output filename. You meed not include the file extension
        baudrate (int, optional): Baud rate for serial communication. Defaults to '9600'
        output_dir (str, optional): Directory to save the output file. Defaults to '.'
        mock (bool, optional): Indicates whether or not serial data should be simulated
        thresh (int, optional): The number of readings gathered before the plot updates

    Returns:
        Tuple(List[float], List[float]): (time_series, voltage_series)
    """
    try:
        # Create the instance and set the port to the users request
        serial_instance = (
            _MockSerial(0.1) if mock else serial.Serial(port=port, baudrate=baudrate)
        )

        # Initialize the output file and its location location
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        name = f"{curr_date}_{name}_{curr_time}"
        os.makedirs(output_dir, exist_ok=True)
        text_name = f"{name}.txt"
        text_path = os.path.join(output_dir, text_name)
        image_name = f"{name}.png"
        image_path = os.path.join(output_dir, image_name)
        print(f"Opening {os.path.abspath(text_path)}")
        print(f"\tCurrent File: {text_name}")

        v_data, t_data = [], []
        t_initial = time.time()

        # Initialize the plot for real time plotting
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 6))
        (line,) = ax.plot([], [], color="blue")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Voltage (V)")
        ax.set_title("Voltage vs. Time")
        ax.grid(True)
        
        num_readings = 0

        with open(text_path, "w") as f:
            while True:
                try:
                    # Read the data from the serial port and add to lists
                    raw = serial_instance.readline().decode().strip()
                    voltage = float(raw)
                    timestamp = time.time() - t_initial

                    v_data.append(voltage)
                    t_data.append(timestamp)
                    f.write(f"{timestamp},{voltage}\n")

                    # Update plot every thresh readings
                    if num_readings == thresh:
                        line.set_xdata(t_data)
                        line.set_ydata(v_data)
                        ax.relim()
                        ax.autoscale_view()
                        fig.canvas.draw()
                        num_readings = 0
                    else:
                        num_readings += 1
                    fig.canvas.flush_events()
                        
                    # Make sure the plot hasn't been manually closed by the user
                    if not plt.fignum_exists(fig.number):
                        print("Plot window closed manually. Stopping...")
                        break
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Data read error: {e}")

        # Finalize the plot and make static
        plt.ioff()
        fig.canvas.draw()
        plt.show()
        print(f"Saving {os.path.abspath(image_path)}")
        print(f"\tCurrent File: {image_name}")
        plt.savefig(image_path)
        plt.close()

        return (t_data, v_data)

    except KeyboardInterrupt:
        plt.ioff()
        fig.canvas.draw()
        plt.show()
        print(f"Saving {os.path.abspath(image_path)}")
        print(f"\tCurrent File: {image_name}")
        plt.savefig(image_path)
        plt.close()

        return (t_data, v_data)
    except Exception as e:
        print(f"Unknown error: {e}")
