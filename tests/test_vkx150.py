import rootlab_lib.vkx150_analysis as vkx150_analysis

file1_in = "../test_data/Height_Ex1.csv"
file1_out = "Height_Ex1"
file2_in = "../test_data/Height_Ex2.csv"
file2_out = "Height_Ex2"
out_dir = "../test_files"

def test_normalize_heightmap1():
    vkx150_analysis.heightmap(file1_in, file1_out, out_dir)
    
def test_normalize_heightmap2():
    vkx150_analysis.heightmap(file2_in, file1_out, out_dir, vertical_axis_label="0 Normalization Iterations", iterations=0)
    vkx150_analysis.heightmap(file2_in, file1_out, out_dir, vertical_axis_label="1 Normalization Iterations", iterations=1)
    
def test_iterations(itr):
    vkx150_analysis.heightmap(file2_in, file1_out, out_dir, vertical_axis_label=f"{itr} Normalization Iterations", iterations=itr, method="bilateral")
    
    
if __name__ == "__main__":
    # test_normalize_heightmap1()
    # test_normalize_heightmap2()
    test_iterations(5)