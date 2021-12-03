import json
import matplotlib.pyplot as plt
from rivertrace.functions import get_pixel_values, parse_netcdf, smooth

lines = [{"file": "data/20210720/reproj_idepix_subset_S2B_MSIL1C_20210720T083559_N0301_R064_T34LDQ_20210720T112210.SAFE.nc", "path": "data/20210720/path.json", "name": "20/07/2021"},
         {"file": "data/20210725/reproj_idepix_subset_S2A_MSIL1C_20210725T083601_N0301_R064_T34LDQ_20210725T104936.SAFE.nc", "path": "data/20210725/path.json", "name": "25/07/2021"},
         {"file": "data/20210730/reproj_idepix_subset_S2B_MSIL1C_20210730T083559_N0301_R064_T34LDQ_20210730T110856.SAFE.nc", "path": "data/20210730/path.json", "name": "30/07/2021"}]
variable = "B8"


fig, ax = plt.subplots(figsize=(18, 10))
ax.set_xlabel("Pixel Length")
ax.set_ylabel(variable)

for line in lines:
    with open(line["path"]) as json_file:
        path = json.load(json_file)
    matrix, lat, lon, mask = parse_netcdf(line["file"], variable)
    y = get_pixel_values(path, matrix)
    y = smooth(y, window_len=200)
    x = range(len(y))
    ax.plot(x, y, label=line["name"])
plt.title("Reflectance (842nm) values along the Chicapa River as it passes the Catoca Mine.")
plt.legend()
plt.tight_layout()
plt.show()
