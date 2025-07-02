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
    output_file_dir: str = "./data/Raw",
    output_image_dir: str = "./data/Series",
    output_image_ext: str = "png",
    mock: bool = False,
    thresh: int = 20,
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
        Tuple(List[float], List[float], str): (voltage_series, time_series, output_file_path)
    """
    try:
        # Create the instance and set the port to the users request
        serial_instance = (
            _MockSerial(0.1) if mock else serial.Serial(port=port, baudrate=baudrate)
        )

        # Initialize the output file and its location location
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        name = f"{curr_date}_{name}_{curr_time}"
        os.makedirs(output_file_dir, exist_ok=True)
        text_name = f"{name}.txt"
        text_path = os.path.join(output_file_dir, text_name)

        os.makedirs(output_image_dir, exist_ok=True)
        image_name = f"{name}.{output_image_ext}"
        image_path = os.path.join(output_image_dir, image_name)
        print(f"Opening {os.path.abspath(text_path)}")
        print(f"\tCurrent File: {text_name}")

        v_data, t_data = [], []
        t_initial = time.time()

        # Initialize the plot for real time plotting
        plt.ion()
        fig, ax = plt.subplots(figsize=(12, 9))
        (line,) = ax.plot([], [], color="blue")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Voltage (V)")
        title = "Voltage vs. Time"
        ax.set_title(title)
        ax.grid(True)

        num_readings = 0

        # Handles closing and saving the plot
        def finalize_and_save_plot():
            line.set_xdata(t_data)
            line.set_ydata(v_data)
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.ioff()
            plt.tight_layout()
            print(f"Saving {os.path.abspath(image_path)}")
            print(f"\tCurrent File: {image_name}")
            plt.savefig(image_path)
            plt.close()

        # If the program exists without updating the plot, it saves a white screen, this ensures the data is saved
        def save_as():
            plt.figure(figsize=(12, 9))
            plt.plot(t_data, v_data, label=title)
            plt.title(title, fontsize=25)
            plt.grid(True)
            plt.xlabel("Time (s)", fontsize=25)
            plt.ylabel("Voltage (V)", fontsize=25)
            plt.tick_params(labelsize=25, width=2, length=7)
            plt.tight_layout()
            plt.savefig(image_path)
            plt.close()

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

        finalize_and_save_plot()
        save_as()
        return (v_data, t_data, text_path)

    except KeyboardInterrupt:
        finalize_and_save_plot()
        save_as()
        return (v_data, t_data, text_path)
    except Exception as e:
        print(f"Unknown error: {e}")
