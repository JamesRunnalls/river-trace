import os
import json
import numpy as np
import matplotlib.pyplot as plt
from rivertrace.functions import get_pixel_values, parse_netcdf, smooth, log

folder_t = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/Tshikapa_L1C_S2_tshikapa_{}_{}_2021-07-{}_2021-07-{}/L2ACOLITE"
path_folder = "data/paths"
variables = [{"key": "TUR_Dogliotti2015", "label": "Turbidity", "title": "Turbidity along the Chicapa River as it passes the Catoca Mine."},
             {"key": "hue_angle", "label": "Hue Angle", "title": "Hue Angle along the Chicapa River as it passes the Catoca Mine."}]

for variable in variables:
    log("Creating plot for variable {}".format(variable["key"]))
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_xlabel("Pixel Length")
    ax.set_ylabel(variable["label"])
    image_bounds = []
    data = {}
    for path in os.listdir(path_folder):
        with open(os.path.join(path_folder, path)) as json_file:
            p = json.load(json_file)
        ps = path.split(".")[0].split("_")
        folder = folder_t.format(ps[1], ps[2], ps[3], ps[3])
        file = list(filter(lambda f: "L2ACOLITE" in f, os.listdir(folder)))[0]
        matrix, lat, lon, mask = parse_netcdf(os.path.join(folder, file), variable["key"])
        data[path.split(".")[0]] = get_pixel_values(p, matrix, min=0, max=10000, group=1)
    sections = list(filter(lambda f: "20" in f, data.keys()))
    sections.sort()
    full_data = {"20":[], "25":[], "30":[]}
    for section in sections:
        max_len = 0
        for fd in full_data.keys():
            s_len = len(data[section.replace("20", fd)])
            if s_len > max_len:
                max_len = s_len
        for fd in full_data.keys():
            new_data = np.ones(max_len)
            new_data[:] = np.nan
            new_data[:len(data[section.replace("20", fd)])] = data[section.replace("20", fd)]
            full_data[fd] = np.concatenate((full_data[fd], new_data))

    for fd in full_data.keys():
        y = smooth(full_data[fd], window_len=400)
        x = range(len(y))
        ax.plot(x, y, label=fd+"-07-2021")

    plt.title(variable["title"])
    plt.legend()
    plt.tight_layout()
    plt.show()
