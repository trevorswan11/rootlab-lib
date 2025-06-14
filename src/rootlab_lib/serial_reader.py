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
    filename: str,
    baudrate: str = 9600,
    output_dir: str = '.',
    mock: bool = False,
) -> Tuple[List[float], List[float]]:
    """
    Reads and plots serial data in real-time, and saves to a timestamped .txt file.

    Args:
        port (str): Serial port (e.g., 'COM3').
        filename (str): Descriptive name used in output filename.
        baudrate (int, optional): Baud rate for serial communication. Defaults to '9600'
        output_dir (str, optional): Directory to save the output file. Defaults to '.'
        mock (bool, optional): Indicates whether or not serial data should be simulated
        
    Returns:
        Tuple(List[float], List[float]): (time_series, voltage_series) 
    """
    try:
        # Create the instance and set the port to the users request
        serial_instance = _MockSerial(0.1) if mock else serial.Serial(port=port, baudrate=baudrate)
        
        # Initialize the output file and its location location
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        filename = f"{curr_date}_{filename}_{curr_time}.txt"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        print(filepath)
        
        v_data, t_data = [], []
        t_initial = time.time()
        
        # Initialize the plot for real time plotting
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 6))
        line, = ax.plot([], [], color='blue')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')
        ax.set_title('Voltage vs. Time')
        ax.grid(True)
        
        with open(filepath, 'w') as f:
            while True:
                try:
                    # Read the data from the serial port and add to lists
                    raw = serial_instance.readline().decode().strip()
                    voltage = float(raw)
                    timestamp = time.time() - t_initial

                    v_data.append(voltage)
                    t_data.append(timestamp)
                    f.write(f"{timestamp},{voltage}\n")

                    # Update plot every frame
                    line.set_xdata(t_data)
                    line.set_ydata(v_data)
                    ax.relim()
                    ax.autoscale_view()
                    fig.canvas.draw()
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
        
        return (t_data, v_data)
        
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")