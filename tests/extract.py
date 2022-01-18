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
        lat_arr_n = np.array(get_pixel_values(p, lat))
        lon_arr_n = np.array(get_pixel_values(p, lon))
        tur_arr_n = np.array(get_pixel_values(p, tur, min=0, max=10000, group=1))
        hue_arr_n = np.array(get_pixel_values(p, hue, group=1))
        box_n = np.array(["{}_{}".format(ps[1], ps[2])] * len(p))

        if len(lat_arr) == 0:
            lat_arr, lon_arr, tur_arr, hue_arr, box = lat_arr_n, lon_arr_n, tur_arr_n, hue_arr_n, box_n
        else:
            dist = 1000000000000
            i_c = 0
            j_c = 0
            for i in range(1, min(50, len(lat_arr)/2)):
                for j in range(len(lat_arr_n)):
                    d = ((lat_arr[-i] - lat_arr_n[j])**2+(lat_arr[-i] - lat_arr_n[j])**2)**0.5
                    if d < dist:
                        dist = d
                        i_c = i
                        j_c = j
            lat_arr = np.concatenate((lat_arr[0:-i_c], lat_arr_n[j_c:]))
            lon_arr = np.concatenate((lon_arr[0:-i_c], lon_arr_n[j_c:]))
            tur_arr = np.concatenate((tur_arr[0:-i_c], tur_arr_n[j_c:]))
            hue_arr = np.concatenate((hue_arr[0:-i_c], hue_arr_n[j_c:]))
            box = np.concatenate((box[0:-i_c], box_n[j_c:]))

    df = pd.DataFrame(list(zip(box, lat_arr, lon_arr, tur_arr, hue_arr)),
                      columns=['Bounding Box', 'Latitude', 'Longitude', 'Turbidity', 'Hue Angle'])
    df.to_csv(os.path.join(out_folder, "data_{}-07-2021.csv".format(date)))





