import rootlab_lib.serial_reader as serial_reader

def test():
    out_dir = "../test_files/"
    serial_reader.gather_pcb_data(
        'COM3', "test", output_file_dir=out_dir, output_image_dir=out_dir,
    )

if __name__ == "__main__":
    test()