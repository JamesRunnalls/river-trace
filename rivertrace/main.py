import os
import json
import numpy as np
from skimage.morphology import skeletonize, thin, remove_small_objects
from rivertrace.functions import log, parse_netcdf, plot_matrix, plot_matrix_select
from rivertrace.functions import classify_water, classify_river, shortest_path


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def trace(file, variable, river, direction="N", threshold=0, buffer=0.01, small_object_size=50, start_jump=0,
          plots=False, small_objects=False, out_folder="", out_file_name="path", jump_path=True, manual_classify=False):
    """
        River tracing for satellite images.

        Parameters:
            file (string): Input satellite image that contains the water detection variable
            variable (string): Name of the variables that defines the water detection layer
            river (string): Path to geojson linestring that defines the rough path of the river
            direction (string): General direction of the river, options N, S, E, W.
            threshold (float): Minimum value that defines a water pixel in the water detection layer
            buffer (float): Distance (in units of lat, lon) from rough path of river that defines a river pixel
            small_objects (bool): Whether to remove small objects
            small_object_size (int): Number of pixels that defines a small object
            start_jump (int): Initial allowable jump between disconnected water pixels
            plots (bool): Plot matrixes for each stage of the processing
            out_folder (string): Path of output folder
            out_file_name (string): Name of output file, defaults to path.json
            jump_path (bool): Include pixels across "jumped" gaps in output path
            manual_classify (bool): Add option for manually removing points from the binary map

        Returns:
            path (list): An array of pixel locations that define the path.
        """

    out_file = os.path.join(out_folder, out_file_name + ".json")
    if os.path.isfile(out_file):
        log("Skipping path creation, output file already exists: {}".format(out_file))
        return

    matrix, lat, lon, mask = parse_netcdf(file, variable)
    bounds = list(np.around(np.array([np.nanmin(lat), np.nanmin(lon), np.nanmax(lat), np.nanmax(lon)]), decimals=2))
    log("Identified image bounds: SW ({},{}) NE ({},{})".format(*bounds), indent=1)

    if plots:
        plot_matrix(matrix, title="Initial plot of {}".format(variable))

    binary = classify_water(matrix, threshold)
    if plots:
        plot_matrix(binary, title="Water classification plot")

    binary, intersects = classify_river(binary, lat, lon, river, buffer=buffer)
    if plots:
        plot_matrix(binary, title="River classification plot")

    if small_objects:
        binary = remove_small_objects(binary, small_object_size)
        if plots:
            plot_matrix(binary, title="Small objects removed")

    if manual_classify:
        binary = plot_matrix_select(binary)

    log("Applying thinning algorithm")
    skel = thin(binary)
    if plots:
        plot_matrix(skel, title="Results of thinning algorithm")

    searching = True
    jump = start_jump
    while searching:
        try:
            path = shortest_path(skel, intersects, direction, jump, jump_path=jump_path)
            searching = False
        except Exception as e:
            if "No path to" in str(e):
                log("Failed to find path with jump value {}".format(jump))
                jump = jump + 5
            else:
                raise

    out = matrix.copy()
    for fp in path:
        out[fp[0], fp[1]] = -100000000
    if plots:
        plot_matrix(out, "Final path plotted on original {} data".format(variable))

    if out_folder != "":
        with open(out_file, 'w') as f:
            json.dump(path, f, cls=NpEncoder)

    log("River trace complete.")
    return path
