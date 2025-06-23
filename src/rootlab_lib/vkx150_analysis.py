"""The main way to interact with data outputted by the source meter in lab."""

import numpy as np
from typing import Tuple, List
import time as t
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

import cv2
from scipy.ndimage import median_filter, gaussian_filter

def heightmap(
    input_filepath: str,
    output_name: str,
    output_dir: str = '.',
    output_image_ext: str = 'png',
    reading_flag_name: str = "Height:",
    horizontal_axis_label: str = "",
    vertical_axis_label: str = "",
    title: str = "VK-x150 Height Heatmap",
    height_unit: str = "",
    iterations: int = 1,
    method: str = "bilateral",
    flatten: bool = True,
) -> List[List[float]]:
    """
    Writes and plots source meter resistance readings vs time and saves a .png of the data.

    Args:
        input_filepath (str): The name of the input file with the data to be read. This should be a csv file.
        output_name (str): Descriptive name used in output filename. The current date and time will be combined with this. Do not include the extension or path
        output_dir (str, optional): The path to be used for the output image. Defaults to '.', the current directory
        output_image_ext (str, optional): The image extension to be used for the output image. You need not include the period. Defaults to 'png'
        reading_flag_name (str, optional): The string to watch for when the actual data is emitted. Defaults to 'Height:'
        horizontal_axis_label (str, optional): The string to use for the x-axis label. Defaults to an empty string
        vertical_axis_label (str, optional): The string to use for the y-axis label. Defaults to an empty string
        title (str, optional): The title of the plot. Defaults to 'VK-x150 Height Heatmap'
        height_unit (str, optional): The unit of the height values reported. Defaults to an empty string
        iterations (int, optional): Determines how many iterations of normalization should occur. This is not lossless and is performance intensive. Cannot be negative (will be clamped to [0, inf]). Defaults to 1
        method (str, optional): Determines the iteration algorithm {"gaussian", "median", "bilateral"}. Defaults to "bilateral"
        flatten (bool, optional): Determines whether or not the program should attempt to correct tilt. Defaults to True
    Returns:
        List[List[float]]: (height_data)
    """
    valid_methods = {"gaussian", "median", "bilateral"}
    if method not in valid_methods:
        raise ValueError(f"Invalid smoothing method '{method}'. Must be one of {valid_methods}.")
    
    # Prep the file system for reading and writing
    if not os.path.isfile(input_filepath):
        print("Error: Input filepath is not a valid file")
        return
    os.makedirs(output_dir, exist_ok=True)
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    output_img = f"{curr_date}_{output_name}_{curr_time}.{output_image_ext}"
    output_img_path = os.path.join(output_dir, output_img)
    
    output_data = f"{curr_date}_{output_name}_{curr_time}.txt"
    output_data_path = os.path.join(output_dir, output_data)
    
    # Initialize the row vectors to hold the differently sized data
    garbage = []
    heights = []
    switch_found = False

    # open the csv file and read in the data until the row length changes
    with open(input_filepath, "r") as f1:
        try:
            reader = csv.reader(f1)
            switch_found = False
            for row in reader:
                if not switch_found:
                    if "".join(row).startswith(reading_flag_name):
                        switch_found = True
                    garbage.append(row)
                    continue  # skip this line and keep going
                # collect height data after the marker
                heights.append(row)
        except Exception as e:
            print(f"Fatal error reading input csv file: {e}")
            return
                
        try:
            for i, row in enumerate(heights):
                heights[i] = np.array([float(value) for value in row if value.strip() != ''], dtype=np.float32)
            
            # Get the average height and shift all values down
            avg_height = np.average(heights)
            for i, row in enumerate(heights):
                heights[i] = np.array([value - avg_height for value in row], dtype=np.float32)
            
            # Get the minimum height and shift the map to be zero'd at that height
            min_height = np.amin(heights)
            for i, row in enumerate(heights):
                heights[i] = np.array([value - min_height for value in row], dtype=np.float32)
                
            height_matrix = np.array(heights, dtype=np.float32)
            
            if flatten:
                height_matrix = _correct_tilt(height_matrix)
            iterations = max(0, iterations)

            if method == "gaussian":
                for idx in range(iterations):
                    height_matrix = gaussian_filter(height_matrix, sigma=1.0)
                    print(f"{method} iteration {idx + 1}: (min, max) = ({np.amin(height_matrix), np.amax(height_matrix)})")

            elif method == "median":
                for idx in range(iterations):
                    height_matrix = median_filter(height_matrix, size=3)
                    print(f"{method} iteration {idx + 1}: (min, max) = ({np.amin(height_matrix), np.amax(height_matrix)})")

            elif method == "bilateral":
                height_matrix = cv2.normalize(height_matrix, None, 0, 255, cv2.NORM_MINMAX)
                height_matrix = np.float32(height_matrix)
                for idx in range(iterations):
                    height_matrix = cv2.bilateralFilter(height_matrix, d=5, sigmaColor=50, sigmaSpace=5)
                    print(f"{method} iteration {idx + 1}: (min, max) = ({np.amin(height_matrix), np.amax(height_matrix)})")

            # Final normalization
            height_matrix -= np.amin(height_matrix)
                    
            with open(output_data_path, 'w') as f:
                print(f"Saving {os.path.abspath(output_data_path)}")
                for row in height_matrix:
                    for i, val in enumerate(row):
                        if (i != len(row)):
                            f.write(f"{val},")
                        else:
                            f.write(f"{val}")
                    f.write("\n")
            
            # Get the final min and max values for a correct cbar scale
            min_height = np.amin(height_matrix)
            max_height = np.amax(height_matrix)
            
            fig, ax = plt.subplots(figsize=(12, 9))
            im = ax.imshow(height_matrix, vmin=min_height, vmax=max_height, cmap="viridis")

            # Labels and axis settings
            ax.set_title(title, fontsize=25, pad=20)
            ax.set_xlabel(horizontal_axis_label, fontsize=15)
            ax.set_ylabel(vertical_axis_label, fontsize=15)
            ax.set_xticks([])
            ax.set_yticks([])

            # Colorbar
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label(f"Height {f"({height_unit})" if height_unit != "" else ""}", fontsize=15)
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((-3, 3))  # Use scientific notation outside this range
            formatter.set_useOffset(False)

            cbar.ax.yaxis.set_major_formatter(formatter)
            cbar.ax.tick_params(labelsize=15)

            plt.tight_layout()
            print(f"Saving {os.path.abspath(output_img_path)}")
            print(f"\tCurrent File: {os.path.basename(output_img_path)}")
            plt.savefig(output_img_path)
            plt.show()
            
            return ()
        except Exception as e:
            print(f"Fatal error plotting height data: {e}")
            return

def _correct_tilt(height_matrix: np.ndarray) -> np.ndarray:
    """Corrects plane tilt. Developed with ChatGPT

    Args:
        height_matrix (np.ndarray): A matrix of height data

    Returns:
        np.ndarray: The corrected matrix of height data
    """
    rows, cols = height_matrix.shape
    X, Y = np.meshgrid(np.arange(cols), np.arange(rows))
    Z = height_matrix

    # Flatten for least squares
    A = np.c_[X.ravel(), Y.ravel(), np.ones(X.size)]
    C, _, _, _ = np.linalg.lstsq(A, Z.ravel(), rcond=None)  # fit Z = ax + by + c
    plane = (C[0] * X + C[1] * Y + C[2])

    # Subtract the plane from the data
    return Z - plane
