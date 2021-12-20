import os
import json
import numpy as np
import matplotlib.pyplot as plt
from rivertrace.functions import get_pixel_values, parse_netcdf, smooth, log

output = "/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/"

dates = [{"date": "30/07/2021", "path_folder": "data/20210730", "data": {"idepix": output+"Tshikapa_L1C_S2__tshikapa_2021-07-30_2021-07-30/L1P",
                                                                         "c2rcc": output+"Tshikapa_L1C_S2__tshikapa_2021-07-30_2021-07-30/L2C2RCC"}},
         {"date": "25/07/2021", "path_folder": "data/20210725", "data": {"idepix": output+"Tshikapa_L1C_S2__tshikapa_2021-07-25_2021-07-25/L1P",
                                                                         "c2rcc": output+"Tshikapa_L1C_S2__tshikapa_2021-07-25_2021-07-25/L2C2RCC"}},
         {"date": "20/07/2021", "path_folder": "data/20210720", "data": {"idepix": output+"Tshikapa_L1C_S2__tshikapa_2021-07-20_2021-07-20/L1P",
                                                                         "c2rcc": output+"Tshikapa_L1C_S2__tshikapa_2021-07-20_2021-07-20/L2C2RCC"}}]

variables = [{"key": "B8", "label": "842nm", "file": "idepix", "title": "Reflectance values along the Chicapa River as it passes the Catoca Mine."},
             {"key": "conc_tsm", "label": "Total Suspended Matter", "file": "c2rcc", "title": "Total Suspended Matter values along the Chicapa River as it passes the Catoca Mine."},
             {"key": "conc_chl", "label": "Chlorophyll A", "file": "c2rcc", "title": "Chlorophyll A values along the Chicapa River as it passes the Catoca Mine."},
             {"key": "rhow_B8A", "label": "865nm", "file": "c2rcc", "title": "Atmospherically corrected Angular dependent water leaving reflectance values along the Chicapa River as it passes the Catoca Mine."}]


variables = [{"key": "rhow_B8A", "label": "865nm", "file": "c2rcc", "title": "Atmospherically corrected Angular dependent water leaving reflectance values along the Chicapa River as it passes the Catoca Mine."}]

for variable in variables:
    log("Creating plot for variable {}".format(variable["key"]))
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_xlabel("Pixel Length")
    ax.set_ylabel(variable["label"])

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
        y = smooth(y, window_len=400)
        x = range(len(y))
        ax.plot(x, y, label=day["date"])
    plt.title(variable["title"])
    plt.legend()
    plt.tight_layout()
    plt.show()
