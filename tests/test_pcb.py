import rootlab_lib.serial_reader as serial_reader
from rootlab_lib.voltage_analysis import _plot_analog_pin_data

def test_gather():
    out_dir = "../test_files/"
    serial_reader.gather_pcb_data(
        'COM3', "test", output_file_dir=out_dir, output_image_dir=out_dir,
    )
    
def test_plot():
    _plot_analog_pin_data("../test_data/data5.txt", 2)

if __name__ == "__main__":
    # test_gather()
    test_plot()