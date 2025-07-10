import os
from typing import List, Tuple
import matplotlib.pyplot as plt
import csv
import time


def _read_numeric_data(
    filepath: str, flag: str = "(s),(mm),(N),(%),(MPa),(N/tex)"
) -> Tuple[
    List[float], List[float], List[float], List[float], List[float], List[float]
]:
    """Reads the data produced by the Instron

    Args:
        filepath (str): The path to the csv file output from the Instron's analysis software
        flag (str, optional): The text to look for to indicate data should be read on the next pass. Defaults to '(s),(mm),(N),(%),(MPa),(N/tex)'

    Returns:
        Tuple[List[float], List[float], List[float], List[float], List[float], List[float],]:
            Time, Extension, Load, Tensile strain (Extension), Tensile stress, Tenacity
    """
    with open(filepath, "r") as f:
        reader = csv.reader(f.readlines())
        read_flag = False

        result = [[], [], [], [], [], []]
        for row in reader:
            if read_flag:
                for i, val in enumerate(row):
                    result[i].append(float(val))
            if ",".join(row) == flag:
                read_flag = True

    return tuple(list(col) for col in result)


def single_stress_strain(
    filepath: str,
    title: str = "Stress-Strain Curve",
    x_label: str = "Tensile Strain (%)",
    y_label: str = "Tensile Stress (MPa)",
    label: str = "Specimen",
    legend: bool = False,
    legend_loc: str = "upper right",
    output_image_dir: str = "./data/Instron",
    output_image_ext: str = "png",
    timestamp: bool = False,
) -> None:
    data = _read_numeric_data(filepath)
    
    name = os.path.splitext(os.path.basename(filepath))[0]
    if timestamp:
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        name = f"{curr_date}_{name}_{curr_time}"
    os.makedirs(output_image_dir, exist_ok=True)
    image_path = os.path.join(output_image_dir, f"{name}.{output_image_ext}")
    
    plt.figure(figsize=(12, 9))
    plt.plot(data[3], data[4], label=label)
    plt.title(title, fontsize=25)
    plt.xlabel(x_label, fontsize=25)
    plt.ylabel(y_label, fontsize=25)
    if legend: 
        plt.legend(loc=legend_loc)
    plt.grid()
    plt.tight_layout()
    print(f"Saving {os.path.abspath(image_path)}")
    print(f"\tCurrent File: {os.path.basename(image_path)}")
    plt.savefig(image_path)
    plt.show()
    
def multiple_stress_strain(
    filepaths: List[str],
    output_filename: str,
    labels: List[str] = [],
    title: str = "Stress-Strain Curves",
    x_label: str = "Tensile Strain (%)",
    y_label: str = "Tensile Stress (MPa)",
    legend: bool = True,
    legend_loc: str = "upper right",
    output_image_dir: str = "./data/Instron",
    output_image_ext: str = "png",
    timestamp: bool = False,
) -> None:
    """Plots multiple stress strain curves on the same plot

    Args:
        filepaths (List[str]): A list of filepaths with data to render
        output_filename (str): The desired name of the output file. You need not specify the extension or include timestamp data. See input `timestamp`
        labels (List[str], optional): The labels for the legend if turned on. Will pad to a numbered list of `Specimen #`. Defaults to [].
        title (str, optional): The title to use for the final plot. Defaults to "Stress-Strain Curve".
        x_label (str, optional): The x-axis label to use. Defaults to "Tensile Strain (%)".
        y_label (str, optional): The y-axis label to use. Defaults to "Tensile Stress (MPa)".
        legend (bool, optional): Whether to show a legend on the final plot. Defaults to True.
        legend_loc (str, optional): The location of the legend. Defaults to "upper right".
        output_image_dir (str, optional): THe directory to automatically save the image to. Defaults to "./data/Instron".
        output_image_ext (str, optional): The extension to use for the generated and saved image. Defaults to "png".
        timestamp (bool, optional): Whether to include the data and time with the saved image to prevent overwriting previously saved plots. Defaults to False.
    """    
    # format the image path
    if timestamp:
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        output_filename = f"{curr_date}_{output_filename}_{curr_time}"
    os.makedirs(output_image_dir, exist_ok=True)
    image_path = os.path.join(output_image_dir, f"{output_filename}.{output_image_ext}")
    
    # Right pad labels to match number of filepaths
    num_files = len(filepaths)
    idx = len(labels) + 1
    while (num_files > len(labels)):
        labels.append(f"Specimen {idx}")
        idx += 1
    
    # collect all of the data
    datum = []
    for filepath in filepaths:
        data = _read_numeric_data(filepath)
        datum.append([data[3], data[4]])
    
    plt.figure(figsize=(12, 9))
    for i in range(len(datum)):
        plt.plot(*datum[i], label=labels[i])
    plt.title(title, fontsize=25)
    plt.xlabel(x_label, fontsize=25)
    plt.ylabel(y_label, fontsize=25)
    if legend: 
        plt.legend(loc=legend_loc)
    plt.grid()
    plt.tight_layout()
    print(f"Saving {os.path.abspath(image_path)}")
    print(f"\tCurrent File: {os.path.basename(image_path)}")
    plt.savefig(image_path)
    plt.show()
        