import os
from rivertrace.main import trace

folder_t = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/Tshikapa_L1C_S2_tshikapa_{}_{}_{}_{}/L2ACOLITE"
out_folder = "data/paths"
water_parameter = "TUR_Dogliotti2015"
river = "data/river.geojson"
direction = "N"

inputs = [["ldq", 2], ["ldr", 4], ["mds", 3], ["mdt", 4], ["mdu", 3]]
dates = ["2021-07-20", "2021-07-25", "2021-07-30", "2021-08-04"]

runs = []
for i in inputs:
    for s in range(1, i[1] + 1):
        for d in dates:
            runs.append({"d": d, "s": s, "i": i[0]})

for run in runs:
    try:
        folder = folder_t.format(run["i"], run["s"], run["d"], run["d"])
        files = list(filter(lambda file: "L2ACOLITE" in file, os.listdir(folder)))
        out_file_name = "path_" + "_".join([str(run["i"]), str(run["s"]), str(run["d"].split("-")[-1])])
        for file in files:
            trace(os.path.join(folder, file), water_parameter, river, direction, threshold=0, start_jump=0, plots=True,
                  out_folder=out_folder, out_file_name=out_file_name, manual_classify=True)
    except Exception as e:
        print("Failed on run: ".format(run))
        print(e)








