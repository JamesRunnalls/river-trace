import os
from rivertrace.main import trace

folder = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/Tshikapa_L1C_S2__tshikapa_2021-07-25_2021-07-25/L2NDWI"
out_folder = "data/20210725"
water_parameter = "swi"
river = "data/river.geojson"
direction = "N"

files = list(filter(lambda file: "L2NDWI" in file, os.listdir(folder)))

trace(os.path.join(folder, files[4]), water_parameter, river, direction, threshold=0.1, start_jump=0, plots=True, out_folder=out_folder)







