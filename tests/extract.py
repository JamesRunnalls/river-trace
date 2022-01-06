import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rivertrace.functions import get_pixel_values, parse_netcdf, smooth, log

folder_t = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/Tshikapa_L1C_S2_tshikapa_{}_{}_2021-07-{}_2021-07-{}/L2ACOLITE"
path_folder = "data/paths"
out_folder = "data/csv"
variables = [{"key": "TUR_Dogliotti2015", "label": "Turbidity", "title": "Turbidity along the Chicapa River as it passes the Catoca Mine."},
             {"key": "hue_angle", "label": "Hue Angle", "title": "Hue Angle along the Chicapa River as it passes the Catoca Mine."}]

paths = os.listdir(path_folder)
paths.sort()

for date in ["20", "25", "30"]:
    dp = [k for k in paths if str(date) in k]
    lat_arr, lon_arr, tur_arr, hue_arr, box = [], [], [], [], []
    for path in dp:
        with open(os.path.join(path_folder, path)) as json_file:
            p = json.load(json_file)
        ps = path.split(".")[0].split("_")
        folder = folder_t.format(ps[1], ps[2], ps[3], ps[3])
        file = list(filter(lambda f: "L2ACOLITE" in f, os.listdir(folder)))[0]
        tur, lat, lon, mask = parse_netcdf(os.path.join(folder, file), "TUR_Dogliotti2015")
        hue, lat, lon, mask = parse_netcdf(os.path.join(folder, file), "hue_angle")
        lat_arr = lat_arr + list(get_pixel_values(p, lat))
        lon_arr = lon_arr + list(get_pixel_values(p, lon))
        tur_arr = tur_arr + list(get_pixel_values(p, tur, min=0, max=10000, group=1))
        hue_arr = hue_arr + list(get_pixel_values(p, hue, group=1))
        box = box + ["{}_{}".format(ps[1], ps[2])] * len(lat)
    df = pd.DataFrame(list(zip(box, lat_arr, lon_arr, tur_arr, hue_arr)),
                      columns=['Bounding Box', 'Latitude', 'Longitude', 'Turbidity', 'Hue Angle'])
    df = df.drop_duplicates(subset=['Latitude', 'Longitude'], keep='first').reset_index(drop=True)
    df.to_csv(os.path.join(out_folder, "data_{}-07-2021.csv".format(date)))





