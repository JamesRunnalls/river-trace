import os
import json
import numpy as np
import matplotlib.pyplot as plt
from rivertrace.functions import get_pixel_values, parse_netcdf, smooth, log

output = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/"

dates = [{"date": "30/07/2021", "color": "red", "path_folder": "data/20210730", "data": {"idepix": output+"Tshikapa_L1C_S2__tshikapa_2021-07-30_2021-07-30/L1P",
                                                                         "c2rcc": output+"Tshikapa_L1C_S2__tshikapa_2021-07-30_2021-07-30/L2C2RCC",
                                                                         "fu": output+"Tshikapa_L1C_S2__tshikapa_2021-07-30_2021-07-30/L2FU"}},
         {"date": "25/07/2021", "color": "purple", "path_folder": "data/20210725", "data": {"idepix": output+"Tshikapa_L1C_S2__tshikapa_2021-07-25_2021-07-25/L1P",
                                                                         "c2rcc": output+"Tshikapa_L1C_S2__tshikapa_2021-07-25_2021-07-25/L2C2RCC",
                                                                         "fu": output+"Tshikapa_L1C_S2__tshikapa_2021-07-25_2021-07-25/L2FU"}},
         {"date": "20/07/2021", "color": "black", "path_folder": "data/20210720", "data": {"idepix": output+"Tshikapa_L1C_S2__tshikapa_2021-07-20_2021-07-20/L1P",
                                                                         "c2rcc": output+"Tshikapa_L1C_S2__tshikapa_2021-07-20_2021-07-20/L2C2RCC",
                                                                         "fu": output+"Tshikapa_L1C_S2__tshikapa_2021-07-20_2021-07-20/L2FU"}}]

variables = [{"key": "B8", "label": "842nm", "file": "idepix", "title": "Reflectance values along the Chicapa River as it passes the Catoca Mine."},
             {"key": "conc_tsm", "label": "Total Suspended Matter", "file": "c2rcc", "title": "Total Suspended Matter values along the Chicapa River as it passes the Catoca Mine."},
             {"key": "conc_chl", "label": "Chlorophyll A", "file": "c2rcc", "title": "Chlorophyll A values along the Chicapa River as it passes the Catoca Mine."},
             {"key": "rhow_B8A", "label": "865nm", "file": "c2rcc", "title": "Atmospherically corrected Angular dependent water leaving reflectance values along the Chicapa River as it passes the Catoca Mine."}]


variables = [{"key": "forel_ule", "label": "Forel-Ule", "file": "fu", "title": "Forel Ule Color Classification along the Chicapa River as it passes the Catoca Mine."},
             {"key": "B8", "label": "842nm", "file": "idepix", "title": "Reflectance values along the Chicapa River as it passes the Catoca Mine."},
             {"key": "hue_angle", "label": "Hue Angle", "file": "fu", "title": "Hue Angle along the Chicapa River as it passes the Catoca Mine."}]

for variable in variables:
    log("Creating plot for variable {}".format(variable["key"]))
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_xlabel("Pixel Length")
    ax.set_ylabel(variable["label"])
    image_bounds = []
    for day in dates:
        log("Processing data for {}".format(day["date"]))
        paths = list(filter(lambda file: "path_" in file, os.listdir(day["path_folder"])))
        paths.sort()
        y = np.array([])
        for path in paths:
            with open(os.path.join(day["path_folder"], path)) as json_file:
                p = json.load(json_file)
            data_files = os.listdir(day["data"][variable["file"]])
            i = [i for i, s in enumerate(data_files) if path.split("_")[1] in s][0]
            matrix, lat, lon, mask = parse_netcdf(os.path.join(day["data"][variable["file"]], data_files[i]), variable["key"])
            y = np.concatenate((y, get_pixel_values(p, matrix)))
            image_bounds.append([len(y), day["color"]])
        y = smooth(y, window_len=800)
        x = range(len(y))
        ax.plot(x, y, label=day["date"], color=day["color"])
    xmin, xmax, ymin, ymax = plt.axis()
    for b in image_bounds:
        ax.plot([b[0], b[0]], [ymin, ymax], color=b[1], alpha=0.3)
    plt.title(variable["title"])
    plt.legend()
    plt.tight_layout()
    plt.show()




    for day in dates:
        log("Processing data for {}".format(day["date"]))
        paths = list(filter(lambda file: day["date"] in file, os.listdir(path_folder)))
        paths.sort()
        y = np.array([])
        for path in paths:
            with open(os.path.join(day["path_folder"], path)) as json_file:
                p = json.load(json_file)
            data_files = os.listdir(day["data"][variable["file"]])
            i = [i for i, s in enumerate(data_files) if path.split("_")[1] in s][0]
            matrix, lat, lon, mask = parse_netcdf(os.path.join(day["data"][variable["file"]], data_files[i]), variable["key"])
            y = np.concatenate((y, get_pixel_values(p, matrix, min=0, max=10000, group=3)))
            image_bounds.append([len(y), day["color"]])
        y = smooth(y, window_len=200)
        x = range(len(y))
        ax.plot(x, y, label=day["date"], color=day["color"])
    xmin, xmax, ymin, ymax = plt.axis()
    for b in image_bounds:
        ax.plot([b[0], b[0]], [ymin, ymax], color=b[1], alpha=0.3)
    plt.title(variable["title"])
    plt.legend()
    plt.tight_layout()
    plt.show()
