import rootlab_lib.dataviz as dataviz
import rootlab_lib.serial_reader as serial_reader

# Tests the serial port reader using a mock instance
def test_reader_mock():
    serial_reader.gather_data(0, 'test.txt', output_dir='../test_files/', mock=True)

threshold = dataviz.RECOMMENDED_THRESHOLD
min_plateau_length = dataviz.RECOMMENDED_MIN_PLATEAU_LENGTH
min_gap_length = dataviz.RECOMMENDED_MIN_GAP_LENGTH

# Tests the 
def test_plot_suite():
    filepath = '../test_files/data1.txt'
    
    dataviz.series(filepath, threshold, min_plateau_length, min_gap_length, title_default='Test Data', title_plateaus='Test Data', plateaus=True)
    dataviz.heatmap(filepath, threshold, min_plateau_length, min_gap_length, title='Test Data')
    dataviz.regression(filepath, threshold, min_plateau_length, min_gap_length, title='Test Data')
    dataviz.regression(filepath, threshold, min_plateau_length, min_gap_length, title='Test Data', intercept=True)
    
if __name__ == '__main__':
    test_reader_mock()
    test_plot_suite()
