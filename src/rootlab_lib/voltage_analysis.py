"""The main plotting suite for analyzing data provided by the arduino."""

from typing import List, Tuple
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import os
from rootlab_lib.plateau_processing import (
    average_voltage_analysis,
    find_plateaus,
    read_timed_voltage_data,
)

# Default values to use thresholds, plateau lengths, and gap lengths
RECOMMENDED_THRESHOLD = 0.05
RECOMMENDED_MIN_PLATEAU_LENGTH = 25
RECOMMENDED_MIN_GAP_LENGTH = 0.01

# ===== Helper Methods for the plotting suite, should be interacted with the main functions at the bottom of this file =====


def _plot_voltage_series(
    time_data: List[float],
    voltage_data: List[float],
    output_file: str,
    output_file_extension: str,
    title: str,
) -> None:
    """Creates a plot of the voltage data against time

    Args:
        time_data (List[float]): The time data from the file
        voltage_data (List[float]): The voltage data from the file
        output_file (str): The output file to save the plot to. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str, optional): The title to use for the plot. Defaults to 'Voltage Series'.

    Returns:
        List[float]: The list of the extracted average values from each plateau
    """
    plt.figure(figsize=(12, 9))
    plt.plot(time_data, voltage_data, label=title)
    plt.title(title, fontsize=25)
    plt.grid(True)
    plt.xlabel("Time (s)", fontsize=25)
    plt.ylabel("Voltage (V)", fontsize=25)
    plt.tick_params(labelsize=25, width=2, length=7)
    output_file = f"{output_file}_SERIES.{output_file_extension}"
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


def _plot_voltage_series_plateaus(
    time_data: List[float],
    voltage_data: List[float],
    plateaus: List[Tuple],
    output_file: str,
    output_file_extension: str,
    title: str,
    legend: bool,
) -> List[float]:
    """Creates a plot of the voltage data and highlights and extracts the average values.

    Args:
        time_data (List[float]): The time data from the file
        voltage_data (List[float]): The voltage data from the file
        plateaus (List[Tuple]): The plateaus calculated and determined through analysis
        output_file (str): The output file to save the plot to. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str): The title to use for the plot. Defaults to 'Voltage Series with Plateaus'.
        legend (bool): Determines whether or not to show the legend. Defaults to False for readability.

    Returns:
        List[float]: The list of the extracted average values from each plateau
    """
    # plot the original series
    plt.figure(figsize=(12, 9))
    plt.plot(time_data, voltage_data, label=title, color="blue")

    # plot each plateau as a scatter, including the average at the average time
    v_avg = []
    for average, start, end in plateaus:
        v_avg.append(average)

        # find the values in each plateau using the start and end
        voltage_values = voltage_data[start:end]
        time_values = time_data[start:end]
        average_time = (time_data[start] + time_data[end - 1]) / 2

        # plot the time and voltage values in the range and add the (avg_time, avg) point
        plt.plot(
            time_values,
            voltage_values,
            label=f"Plateau: {average_time:.2f}s, Avg: {average:.2f}V",
            color="red",
        )
        plt.scatter(average_time, average, color="black", zorder=5)

    # format the plot for readers convenience
    plt.title("Voltage Series with Plateaus")
    plt.grid(True)
    plt.xlabel("Increment", fontsize=25)
    plt.ylabel("Voltage", fontsize=25)
    plt.tick_params(labelsize=25, width=2, length=7)
    if legend:
        plt.legend()

    # show the plot and return the average voltages
    output_file = f"{output_file}_SERIES-plats.{output_file_extension}"
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()

    return v_avg


def _plot_voltage_heatmap(
    V_avg_map: np.ndarray, output_file: str, output_file_extension: str, title: str
) -> None:
    """Plots an analysis of the data as a heatmap

    Args:
        V_avg_map (np.ndarray): The average voltages
        output_file (str): The output file to save the plot. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str): The title of the plot to show. Defaults to 'Voltage Heatmap'
    """
    # Add the data to the figure
    plt.figure(figsize=(12, 9))
    plt.imshow(V_avg_map, vmin=0, vmax=5, cmap="viridis")
    plt.xticks(tuple(i for i in range(0, 7)))

    # Plot the voltage series with labeled axes and colors for presentation
    plt.xlabel("Position (0.5 cm)", fontsize=25)
    plt.ylabel("Position (0.5 cm)", fontsize=25)
    plt.title(title, fontsize=25)
    cbar = plt.colorbar()
    cbar.set_label("Voltage (V)", fontsize=25)
    cbar.ax.tick_params(labelsize=25)
    plt.tick_params(labelsize=25, width=3, length=7)
    plt.tight_layout()
    output_file = f"{output_file}_HEATMAP.{output_file_extension}"
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


def _plot_voltage_regression(
    pos: np.ndarray,
    V_avg_column: np.ndarray,
    V_std_column: np.ndarray,
    output_file: str,
    output_file_extension: str,
    title: str,
    intercept: bool,
) -> None:
    """Plots an analysis of the data as a heatmap

    Args:
        pos (np.ndarray): The x-axis positions of the voltages to display on the regression and to use in the regression analysis
        V_avg_column (np.ndarray): The y-axis positions of the voltages to display
        V_std_column (np.ndarray): The standard deviation of of each voltage reading, to be used in error bar plotting
        output_file (str): The output file to save the plot to. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str): The title of the plot to show
        intercept (bool): Determines if the y-intercept should be variable and not fixed at (0,0)
    """
    # Plot the average data for statistical analysis
    pos_full = np.array([0.0, 0.25, 0.75, 1.25, 1.75, 2.25, 3.0], dtype=float)
    plt.title(title, fontsize=25)
    plt.xlabel("Position (cm)", fontsize=25)
    plt.ylabel("Voltage (V)", fontsize=25)
    plt.tick_params(labelsize=25, width=2, length=7)
    plt.ylim((-0.9, 5.1))
    plt.xlim((-0.1, 3.1))
    plt.errorbar(
        pos, V_avg_column, yerr=V_std_column, linestyle="None", marker="o", color="k"
    )
    if intercept:
        res = stats.linregress(pos, V_avg_column)
        plt.plot(
            pos_full,
            res[0] * pos_full + res[1],
            "r",
            label="V = %.2f x + %.2f\nR$^2$= %.4f" % (res[0], res[1], res[2] ** 2),
        )
    else:
        res = np.polyfit(pos, V_avg_column, 1, w=np.ones_like(pos), full=True)
        slope = res[0][0]
        residuals = res[1][0] if len(res[1]) > 0 else 0
        r2 = 1 - (residuals / np.sum((V_avg_column - np.mean(V_avg_column)) ** 2))
        plt.plot(
            pos_full,
            slope * pos_full,
            "r",
            label="V = %.2f x\nR$^2$= %.4f" % (slope, r2),
        )
    plt.legend(loc="upper left", frameon=False, fontsize=20)
    output_file = (
        f"{output_file}_REGRESSION-intercept.{output_file_extension}"
        if intercept
        else f"{output_file}_REGRESSION.{output_file_extension}"
    )
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


# ===== The main functions for the user to interface with =====


def heatmap(
    filepath: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    title: str = "Heatmap",
    prepend_zero: bool = False,
    output_dir: str = ".",
    output_image_extension: str = "png",
) -> None:
    """Creates a heatmap out of given data

    Args:
        filepath (str): The file to use formatted as [time_series, voltage]
        threshold (float, optional): The minimum voltage to be considered for a plateau. Defaults to 0.05
        min_plateau_length (float, optional): The minimum length of a plateau to be logged. Defaults to 25
        min_gap_length (float, optional): The minimum voltage drop to break a plateau. Defaults to 0.01
        title (str, optional): The title to use for the map. Defaults to 'Heatmap'.
        prepend_zero (bool, optional): Determines if the plateaus should have 0 added to the start of the list. Defaults to False.
        output_dir (str, optional): The directory to save the image to. Defaults to '.', the current directory
        output_image_extension (str, optional): Specifies the image type to save the generated graph as. Do not include the dot. Defaults to png
    """
    v_averages = [
        v_avg
        for v_avg, _, _ in find_plateaus(
            read_timed_voltage_data(filepath)[1],
            threshold,
            min_plateau_length,
            min_gap_length,
        )
    ]
    if prepend_zero:
        v_averages = [0] + v_averages
    print(f"{v_averages}\n Number of Plateaus: {len(v_averages)}")
    basename = os.path.basename(filepath)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}")
    _plot_voltage_heatmap(
        average_voltage_analysis(v_averages)[1],
        output_file,
        output_image_extension,
        title,
    )


def regression(
    filepath: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    title: str = "Regression Model",
    prepend_zero: bool = False,
    intercept: bool = False,
    output_dir: str = ".",
    output_image_extension: str = "png",
) -> None:
    """Creates a linear regression out of given data

    Args:
        filepath (str): The file to use formatted as [time_series, voltage]
        threshold (float, optional): The minimum voltage to be considered for a plateau. Defaults to 0.05
        min_plateau_length (float, optional): The minimum length of a plateau to be logged. Defaults to 25
        min_gap_length (float, optional): The minimum voltage drop to break a plateau. Defaults to 0.01
        title (str, optional): The title to use for the plot. Defaults to 'Regression Model'.
        prepend_zero (bool, optional): Determines if the plateaus should have 0 added to the start of the list. Defaults to False.
        intercept (bool, optional): Determines if the y-intercept should be variable and not fixed at (0,0). Defaults to False.
        output_dir (str, optional): The directory to save the image to. Defaults to '.', the current directory
        output_image_extension (str, optional): Specifies the image type to save the generated graph as. Do not include the dot. Defaults to png
    """
    data = read_timed_voltage_data(filepath)
    v_averages = [
        v_avg
        for v_avg, _, _ in find_plateaus(
            data[1], threshold, min_plateau_length, min_gap_length
        )
    ]
    if prepend_zero:
        v_averages = [0] + v_averages
    pos, _, V_avg_column, V_std_column = average_voltage_analysis(v_averages)
    basename = os.path.basename(filepath)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}")
    _plot_voltage_regression(
        pos,
        V_avg_column,
        V_std_column,
        output_file,
        output_image_extension,
        title,
        intercept,
    )


def series(
    filepath: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    title_default: str = "Voltage Series",
    title_plateaus: str = "Voltage Series with Plateaus",
    plateaus: bool = False,
    legend: bool = False,
    output_series_dir: str = "./data/Series",
    output_plats_dir: str = "./data/Plats",
    output_image_extension: str = "png",
) -> None:
    """Creates the voltage series out of given data

    Args:
        filepath (str): The file to use formatted as [time_series, voltage]
        threshold (float, optional): The minimum voltage to be considered for a plateau. Defaults to 0.05
        min_plateau_length (float, optional): The minimum length of a plateau to be logged. Defaults to 25
        min_gap_length (float, optional): The minimum voltage drop to break a plateau. Defaults to 0.01
        title_default (str, optional): The title to use for the map. Defaults to 'Voltage Series'.
        title_plateaus (str, optional): The title to use for the map. Defaults to 'Voltage Series with Plateaus'.
        plateaus (bool, optional): Determines if the plateaus should be plotted on the graph. Defaults to False.
        legend (bool, optional): Determines whether or not to show the legend. Defaults to False for readability.
        output_series_dir (str, optional): The directory to save the image to if the plateau flag is false. Defaults to '.', relative to the current directory
        output_plats_dir (str, optional): The directory to save the image to if the plateau flag is true. Defaults to './data/Plats', relative to the current directory
        output_image_extension (str, optional): Specifies the image type to save the generated graph as. Do not include the dot. Defaults to png
    """
    data = read_timed_voltage_data(filepath)
    plats = find_plateaus(data[1], threshold, min_plateau_length, min_gap_length)
    basename = os.path.basename(filepath)

    output_dir = output_plats_dir if plateaus else output_series_dir
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}")

    if plateaus:
        _plot_voltage_series_plateaus(
            data[0],
            data[1],
            plats,
            output_file,
            output_image_extension,
            title_plateaus,
            legend,
        )
    else:
        _plot_voltage_series(
            data[0],
            data[1],
            output_file,
            output_image_extension,
            title_default,
        )
