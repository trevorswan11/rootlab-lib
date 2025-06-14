from typing import List
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from rootlab_lib.plateau_processing import average_voltage_analysis, find_plateaus, read_timed_voltage_data

# Default values to use thresholds, plateau lengths, and gap lengths
RECOMMENDED_THRESHOLD = 0.05
RECOMMENDED_MIN_PLATEAU_LENGTH = 25
RECOMMENDED_MIN_GAP_LENGTH = 0.01

def plot_voltage_series(time_data: List[float], voltage_data: List[float], title: str = 'Voltage Series') -> None:
    """Creates a plot of the voltage data against time

    Args:
        time_data (List[float]): The time data from the file
        voltage_data (List[float]): The voltage data from the file
        legend (bool, optional): Determines whether or not to show the legend. Defaults to False for readability.
        title (str, optional): The title to use for the plot. Defaults to 'Voltage Series'.

    Returns:
        List[float]: The list of the extracted average values from each plateau
    """    
    plt.figure(figsize=(12,6))
    plt.plot(time_data, voltage_data, label=title)    
    plt.title(title, fontsize=25)
    plt.grid(True)
    plt.xlabel('Time (s)', fontsize=25)
    plt.ylabel('Voltage (V)', fontsize=25)
    plt.tick_params(labelsize=25, width=2, length=7)
    plt.show()

def plot_voltage_series_plateaus(time_data: List[float], voltage_data: List[float], plateaus: List[tuple], title: str = 'Voltage Series with Plateaus', legend: bool = False) -> List[float]:
    """Creates a plot of the voltage data and highlights and extracts the average values.

    Args:
        time_data (List[float]): The time data from the file
        voltage_data (List[float]): The voltage data from the file
        plateaus (List[tuple]): The plateaus calculated and determined through analysis
        title (str, optional): The title to use for the plot. Defaults to 'Voltage Series with Plateaus'.
        legend (bool, optional): Determines whether or not to show the legend. Defaults to False for readability.

    Returns:
        List[float]: The list of the extracted average values from each plateau
    """    
    # plot the original series
    plt.figure(figsize=(12,6))
    plt.plot(time_data, voltage_data, label=title, color='blue')
    
    # plot each plateau as a scatter, including the average at the average time
    v_avg = []
    for average, start, end in plateaus:
        v_avg.append(average)
        
        # find the values in each plateau using the start and end
        voltage_values = voltage_data[start:end]
        time_values = time_data[start:end]
        average_time = (time_data[start] + time_data[end - 1]) / 2
        
        # plot the time and voltage values in the range and add the (avg_time, avg) point 
        plt.plot(time_values, voltage_values, label=f"Plateau: {average_time:.2f}s, Avg: {average:.2f}V", color='red')
        plt.scatter(average_time, average, color='black', zorder=5)
        
    # format the plot for readers convenience
    plt.title('Voltage Series with Plateaus')
    plt.grid(True)
    plt.xlabel('Increment', fontsize=25)
    plt.ylabel('Voltage', fontsize=25)
    plt.tick_params(labelsize=25, width=2, length=7)
    if legend: plt.legend()
    
    # show the plot and return the average voltages
    plt.show()
    return v_avg

def plot_voltage_heatmap(V_avg_map: np.ndarray, title: str = 'Voltage Heatmap') -> None:
    """Plots an analysis of the data as a heatmap

    Args:
        V_avg_map (np.ndarray): The average voltages
    """        
    # Add the data to the figure
    plt.figure(figsize=(12,9))
    plt.imshow(V_avg_map, vmin=0, vmax=5, cmap='viridis')
    plt.xticks(tuple(i for i in range(0, 7)))
    
    # Plot the voltage series with labeled axes and colors for presentation
    plt.xlabel('Position (0.5 cm)', fontsize=25)
    plt.ylabel('Position (0.5 cm)', fontsize=25)
    plt.title(title, fontsize=25)
    cbar = plt.colorbar()
    cbar.set_label('Voltage (V)', fontsize=25)
    cbar.ax.tick_params(labelsize=25)
    plt.tick_params(labelsize=25, width=3, length=7)
    plt.tight_layout()
    plt.show()

# TODO: Add a plot_multiple_voltage_heatmaps function
def plot_multiple_voltage_heatmaps(V_maps: list, titles: list = None) -> None:
    """Plots multiple voltage heatmaps in a single figure with subplots.

    Args:
        V_maps (list of np.ndarray): List of 2D numpy arrays representing voltage maps.
        titles (list of str, optional): List of titles for each heatmap. Defaults to generic numbering if None.
    """    
    n = len(V_maps)  # Number of heatmaps
    titles = titles if titles else [f'Voltage Heatmap {i+1}' for i in range(n)]
    
    fig, axes = plt.subplots(n, 1, figsize=(12, 9 * n), constrained_layout=True)

    # Ensure axes is iterable (in case there's only one plot)
    if n == 1:
        axes = [axes]

    for i, (V_map, title) in enumerate(zip(V_maps, titles)):
        im = axes[i].imshow(V_map, vmin=0, vmax=5, cmap='viridis')
        axes[i].set_xticks(tuple(range(0, 7)))
        axes[i].set_xlabel('Position (0.5 cm)', fontsize=25)
        axes[i].set_ylabel('Position (0.5 cm)', fontsize=25)
        axes[i].set_title(title, fontsize=25)
        axes[i].tick_params(labelsize=25, width=3, length=7)

        # Add colorbar to each subplot
        cbar = fig.colorbar(im, ax=axes[i])
        cbar.set_label('Voltage (V)', fontsize=25)
        cbar.ax.tick_params(labelsize=25)

    plt.show()
        
    
def plot_voltage_regression(pos: np.ndarray, V_avg_column: np.ndarray, V_std_column: np.ndarray, title: str = 'Regression Model', intercept: bool = False) -> None:
    # Plot the average data for statistical analysis
    pos_full = np.array([0.0, 0.25, .75, 1.25, 1.75, 2.25, 3.0], dtype=float)
    plt.title(title, fontsize=25)
    plt.xlabel('Position (cm)', fontsize=25)
    plt.ylabel('Voltage (V)', fontsize=25)
    plt.tick_params(labelsize=25, width=2, length=7)
    plt.ylim((-0.9,5.1))
    plt.xlim((-0.1,3.1))
    plt.errorbar(pos, V_avg_column, yerr=V_std_column,
             linestyle='None', marker='o', color='k')
    if intercept:
        res = stats.linregress(pos, V_avg_column)
        plt.plot(pos_full, res[0]*pos_full + res[1], 'r', label='V = %.2f x + %.2f\nR$^2$= %.4f' % (res[0], res[1], res[2]**2))
    else:
        res = np.polyfit(pos, V_avg_column, 1, w=np.ones_like(pos), full=True)
        slope = res[0][0]
        residuals = res[1][0] if len(res[1]) > 0 else 0
        r2 = 1 - (residuals / np.sum((V_avg_column - np.mean(V_avg_column))**2))
        plt.plot(pos_full, slope*pos_full, 'r', label='V = %.2f x\nR$^2$= %.4f' % (slope, r2))
    plt.legend(loc='upper left', frameon=False, fontsize=20)
    plt.show()

def heatmap(filename: str, threshold: float, min_plateau_length: float, min_gap_length: float, title: str = 'Heatmap', prepend_zero: bool = False):
    """Creates a heatmap out of given data

    Args:
        filename (str): The file to use formatted as [time_series, voltage]
        threshold (float): The minimum voltage to be considered for a plateau
        min_plateau_length (float): The minimum length of a plateau to be logged
        min_gap_length (float): The minimum voltage drop to break a plateau
        title (str, optional): The title to use for the map. Defaults to 'Heatmap'.
        prepend_zero (bool, optional): Determines if the plateaus should have 0 added to the start of the list. Defaults to False.
    """
    v_averages = [v_avg for v_avg, _, _  in find_plateaus(read_timed_voltage_data(filename)[1], threshold, min_plateau_length, min_gap_length)]
    if prepend_zero:
        v_averages = [0] + v_averages
    print(f"{v_averages}\n Number of Plateaus: {len(v_averages)}")
    plot_voltage_heatmap(
        average_voltage_analysis(v_averages)[1], title
    )
    
def regression(filename: str, threshold: float, min_plateau_length: float, min_gap_length: float, title: str = 'Regression Model', prepend_zero: bool = False, intercept: bool = False):
    """Creates a linear regression out of given data

    Args:
        filename (str): The file to use formatted as [time_series, voltage]
        threshold (float): The minimum voltage to be considered for a plateau
        min_plateau_length (float): The minimum length of a plateau to be logged
        min_gap_length (float): The minimum voltage drop to break a plateau
        title (str, optional): The title to use for the plot. Defaults to 'Regression Model'.
        prepend_zero (bool, optional): Determines if the plateaus should have 0 added to the start of the list. Defaults to False.
        intercept (bool, optional): Determines if the y-intercept should be variable and not fixed at (0,0). Defaults to False.
    """
    data = read_timed_voltage_data(filename)
    v_averages = [v_avg for v_avg, _, _  in find_plateaus(data[1], threshold, min_plateau_length, min_gap_length)]
    if prepend_zero:
        v_averages = [0] + v_averages
    pos, _, V_avg_column, V_std_column = average_voltage_analysis(v_averages)
    plot_voltage_regression(pos, V_avg_column, V_std_column, title=title, intercept=intercept)
    
def series(filename: str, threshold: float, min_plateau_length: float, min_gap_length: float, title_default: str = 'Voltage Series', title_plateaus: str = 'Voltage Series with Plateaus', plateaus: bool = False, legend: bool = False):
    """Creates the voltage series out of given data

    Args:
        filename (str): The file to use formatted as [time_series, voltage]
        threshold (float): The minimum voltage to be considered for a plateau
        min_plateau_length (float): The minimum length of a plateau to be logged
        min_gap_length (float): The minimum voltage drop to break a plateau
        title_default (str, optional): The title to use for the map. Defaults to 'Voltage Series'.
        title_plateaus (str, optional): The title to use for the map. Defaults to 'Voltage Series with Plateaus'.
        plateaus (bool, optional): Determines if the plateaus should be plotted on the graph. Defaults to False.
        legend (bool, optional): Determines whether or not to show the legend. Defaults to False for readability.
    """
    data = read_timed_voltage_data(filename)
    plats = find_plateaus(data[1], threshold, min_plateau_length, min_gap_length)
    
    if (plateaus):
        plot_voltage_series_plateaus(data[0], data[1], plats, title_plateaus, legend)
    else:
        plot_voltage_series(data[0], data[1], title_default)
        
