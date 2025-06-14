import rootlab_lib.source_meter_analysis as source_meter_analysis


def test_data():
    test_file = "../test_files/data2.csv"
    output_png = "../test_files/data2_SOURCE-METER.png"
    source_meter_analysis.gather_data(test_file, output_png)


if __name__ == "__main__":
    test_data()
