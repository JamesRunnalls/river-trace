import numpy as np
import matplotlib.pyplot as plt
from rivertrace import trace
from rivertrace.functions import plot_matrix, parse_netcdf, log, classify_river, plot_matrix_select, get_pixel_values

turb = "data/turbidity.nc"
swi = "data/swi.nc"
rough_river = "data/river.geojson"

swi_data, lat, lon = parse_netcdf(swi, "rhos_swi", "lat", "lon")
plot_matrix(swi_data, title="SWI")

log("Reading data from file {}".format(turb))
matrix, lat, lon = parse_netcdf(turb, "turb", "lat", "lon")

log("Create boolean pixel map of water/ non-water pixels")
boolean = matrix.copy()
boolean[boolean == 0] = np.nan
boolean[~np.isnan(boolean)] = True
boolean[np.isnan(boolean)] = False
boolean = boolean.astype(bool)
plot_matrix(boolean, title="Water classification plot")

log("Update boolean pixel map to river pixels by applying max distance from rough river path")
boolean, start, end = classify_river(boolean, lat, lon, rough_river, buffer=0.001, direction="N")
plot_matrix(boolean, title="River classification plot")

log("Manually remove any incorrectly classified water pixels")
boolean = plot_matrix_select(boolean)

path = trace(boolean, start, end)

log("Plot results")
output = swi_data.copy()
for p in path:
    output[p[0], p[1]] = 2

plot_matrix(output, title="River classification plot")

log("Plot profile of input values")
values = np.array(get_pixel_values(path, matrix, min=0, max=10000, group=1))
plt.plot(values)
plt.show()
