import rootlab_lib.voltage_analysis as voltage_analysis
import rootlab_lib.serial_reader as serial_reader

# Tests the serial port reader using a mock instance
def test_reader_mock():
    serial_reader.gather_data(0, 'test', output_dir='../test_files/', mock=True)

# These are the values used as defaults for the series, heatmap, and regression functions
threshold = voltage_analysis.RECOMMENDED_THRESHOLD
min_plateau_length = voltage_analysis.RECOMMENDED_MIN_PLATEAU_LENGTH
min_gap_length = voltage_analysis.RECOMMENDED_MIN_GAP_LENGTH

# Tests the 
def test_plot_suite():
    filepath = '../test_files/data1.txt'
    
    voltage_analysis.series(filepath, title_default='Test Data', title_plateaus='Test Data')
    voltage_analysis.series(filepath, title_default='Test Data', title_plateaus='Test Data', plateaus=True)
    voltage_analysis.heatmap(filepath, title='Test Data')
    voltage_analysis.regression(filepath, title='Test Data')
    voltage_analysis.regression(filepath, title='Test Data', intercept=True)
    
if __name__ == '__main__':
    test_reader_mock()
    test_plot_suite()
