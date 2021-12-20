import os
from rivertrace.main import trace

folder = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/Tshikapa_L1C_S2__tshikapa_2021-07-20_2021-07-20/L2NDWI"
out_folder = "data/20210720"
water_parameter = "swi"
river = "data/river.geojson"
direction = "N"

files = list(filter(lambda file: "L2NDWI" in file, os.listdir(folder)))

for file in files:
    trace(os.path.join(folder, file), water_parameter, river, direction, threshold=0, start_jump=0, plots=True, out_folder=out_folder)















