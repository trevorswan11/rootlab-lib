"""The main way to interact with data outputted by the arduino in lab."""

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import os
from typing import List, Tuple
import random
import threading
import queue


class _MockSerialBasic:
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
    title: str = "Voltage vs. Time",
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
        output_image_ext (str, optional): Extension to use for the output image. You need not include the period. Defaults to 'png'
        title (str, optional): The title to use for the plot. Defaults to 'Voltage vs. Time'
        mock (bool, optional): Indicates whether or not serial data should be simulated
        thresh (int, optional): The number of readings gathered before the plot updates

    Returns:
        Tuple(List[float], List[float], str): (voltage_series, time_series, output_file_path)
    """
    try:
        # Create the instance and set the port to the users request
        serial_instance = (
            _MockSerialBasic(0.1) if mock else serial.Serial(port=port, baudrate=baudrate)
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

class _MockSerialPCB:
    """Simulates a PCB based serial.Serial interface."""

    def __init__(self, delay=0.1):
        self.delay = delay

    def readline(self):
        time.sleep(self.delay)
        return f"{random.uniform(0, 5):.3f},{random.uniform(0, 5):.3f},{random.uniform(0, 5):.3f},{random.choice(['T', 'B'])}\n".encode()
    
class PCBDataOut:
    def __init__(self, vt1, vt2, vt3, vb1, vb2, vb3, t, t1, t2, index, *args):
        self.VT = vt1
        self.VT2 = vt2
        self.VT3 = vt3
        self.VB = vb1
        self.VB2 = vb2
        self.VB3 = vb3
        self.t = t
        self.t1 = t1
        self.t2 = t2
        self.index = index
        self.store = args
        
def gather_pcb_data(
    port: str,
    name: str,
    baudrate: str = 115200,
    output_file_dir: str = "./data/Raw",
    output_image_dir: str = "./data/Series",
    output_image_ext: str = "png",
    title_drives: str = "Top/Bottom Drive",
    title_senses: str = "VT1, VT2, VT3",
    mock: bool = False,
    thresh: int = 1000,
) -> Tuple[PCBDataOut, str]:
    """
    Reads and plots serial data in real-time, and saves to a timestamped .txt file.

    Args:
        port (str): Serial port (e.g., 'COM3').
        name (str): Descriptive name used in output filename. You need not include the file extension
        baudrate (int, optional): Baud rate for serial communication. Defaults to '9600'
        output_file_dir (str, optional): Directory to save the output file. Defaults to '.', the current directory
        output_image_dir (str, optional): Directory to save the output image. Defaults to '.', the current directory
        output_image_ext (str, optional): Extension to use for the output image. You need not include the period. Defaults to 'png'
        title_drives (str, optional): The title to use for the drive layer's plot. Defaults to "Top/Bottom Drive"
        title_drives (str, optional): The title to use for the sense layer's plot. Defaults to "VT1, VT2, VT3"
        mock (bool, optional): Indicates whether or not serial data should be simulated
        thresh (int, optional): The number of readings gathered before the plot updates

    Returns:
        Tuple(PCBDataOut, str): (PCBDataOut[VT, VT2, VT3, VB, VB2, VB3, t, t1, t2, index], output_file_path)
    """
    ser = _MockSerialPCB(0.1) if mock else serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
    curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
    base_name = f"{curr_date}_{name}_{curr_time}"

    os.makedirs(output_file_dir, exist_ok=True)
    text_path = os.path.join(output_file_dir, f"{base_name}.txt")
    os.makedirs(output_image_dir, exist_ok=True)
    image_path = os.path.join(output_image_dir, f"{base_name}.{output_image_ext}")

    print(f"Recording to: {os.path.abspath(text_path)}")

    VT, VT2, VT3 = [], [], []
    VB, VB2, VB3 = [], [], []
    t, t1, t2 = [], [], []
    index = []
    t0 = time.time()

    data_queue = queue.Queue()

    # === Background thread to read serial data ===
    def serial_reader(ser_instance: serial.Serial):
        with open(text_path, "w") as f:
            while True:
                try:
                    raw = ser_instance.readline().decode().strip().split(",")
                    if len(raw) != 4:
                        continue
                    timestamp = time.time() - t0
                    f.write(",".join(raw[:3]) + f",{timestamp:.3f},{raw[3]}\n")
                    f.flush()
                    data_queue.put((timestamp, raw))
                except Exception as e:
                    print("Read error:", e)
                    break

    reader_thread = threading.Thread(target=serial_reader, args=(ser,), daemon=True)
    reader_thread.start()

    # === Setup plot ===
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    ax1.set_title(title_drives)
    ax2.set_title(title_senses)
    ax1.set_ylabel("Voltage (V)")
    ax2.set_ylabel("Voltage (V)")
    ax2.set_xlabel("Time (s)")

    line_top, = ax1.plot([], [], label="Top Drive")
    line_bottom, = ax1.plot([], [], label="Bottom Drive")
    ax1.legend(loc='upper right')

    line_vt1, = ax2.plot([], [], label="VT1")
    line_vt2, = ax2.plot([], [], label="VT2")
    line_vt3, = ax2.plot([], [], label="VT3")
    ax2.legend(loc='upper right')

    def update_plot(_):
        updated = False
        while not data_queue.empty():
            timestamp, raw = data_queue.get()
            try:
                v1 = float(raw[0])
                v2 = float(raw[1])
                v3 = float(raw[2])
                flag = raw[3]

                if flag == "T":
                    VT.append(v1)
                    VT2.append(v2)
                    VT3.append(v3)
                    t1.append(timestamp)
                elif flag == "B":
                    VB.append(v1)
                    VB2.append(v2)
                    VB3.append(v3)
                    t2.append(timestamp)
                t.append(timestamp)
                index.append(flag)
                updated = True
                
                if not updated:
                    return
            
            except Exception as e:
                print("Parse error:", e)

        # Plot trimmed to `thresh`
        line_top.set_data(t1[-thresh:], VT2[-thresh:])
        line_bottom.set_data(t2[-thresh:], VB2[-thresh:])
        line_vt1.set_data(t1[-thresh:], VT[-thresh:])
        line_vt2.set_data(t1[-thresh:], VT2[-thresh:])
        line_vt3.set_data(t1[-thresh:], VT3[-thresh:])

        for ax in [ax1, ax2]:
            ax.relim()
            ax.autoscale_view()

    global ani
    ani = animation.FuncAnimation(fig, update_plot, interval=100, cache_frame_data=False)
    plt.tight_layout()
    try:
        plt.show()
    except KeyboardInterrupt:
        print("Plot window closed manually. Stopping...")
    except Exception as e:
        print("Plotting failed. Stopping...")

    fig.savefig(image_path)
    print(f"Plot saved to {image_path}")
    reader_thread.join(0.1)
    return PCBDataOut(VT, VT2, VT3, VB, VB2, VB3, t, t1, t2, index, ani), text_path