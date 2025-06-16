import rootlab_lib.source_meter_analysis as source_meter_analysis


def test_data():
    test_filepath = "../test_files/data2.csv"
    output_name = "data2_SOURCE-METER"
    source_meter_analysis.gather_data(test_filepath, output_name, '../test_files/')


if __name__ == "__main__":
    test_data()
