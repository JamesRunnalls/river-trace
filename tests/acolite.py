import os
from rivertrace.main import trace

folder_t = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/Tshikapa_L1C_S2_tshikapa_{}_{}_2021-07-{}_2021-07-{}/L2ACOLITE"
out_folder = "data/paths"
water_parameter = "TUR_Dogliotti2015"
river = "data/river.geojson"
direction = "N"

runs = [{"d": 20, "s": 1, "i": "ldq"},
        {"d": 25, "s": 1, "i": "ldq"},
        {"d": 30, "s": 1, "i": "ldq"},
        {"d": 20, "s": 2, "i": "ldq"},
        {"d": 25, "s": 2, "i": "ldq"},
        {"d": 30, "s": 2, "i": "ldq"}]

for run in runs:
    folder = folder_t.format(run["i"], run["s"], run["d"], run["d"])
    files = list(filter(lambda file: "L2ACOLITE" in file, os.listdir(folder)))
    out_file_name = "path_" + "_".join([str(run["i"]), str(run["s"]), str(run["d"])])
    for file in files:
        trace(os.path.join(folder, file), water_parameter, river, direction, threshold="None", start_jump=0, plots=False,
              out_folder=out_folder, out_file_name=out_file_name)







