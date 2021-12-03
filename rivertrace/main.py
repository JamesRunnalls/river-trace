import json
import numpy as np
from skimage.morphology import skeletonize, thin, remove_small_objects
from rivertrace.functions import parse_netcdf, plot_matrix, classify_water, classify_river, shortest_path, plot_graph, log


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
          plots=False, small_objects=False, out_file=""):
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
            out_file (string): Path of output file

        Returns:
            path (list): An array of pixel locations that define the path.
        """
    matrix, lat, lon, mask = parse_netcdf(file, variable)
    if plots:
        plot_matrix(matrix)

    binary = classify_water(matrix, threshold)
    if plots:
        plot_matrix(binary)

    binary, intersects = classify_river(binary, lat, lon, river, buffer=buffer)
    if plots:
        plot_matrix(binary)

    if small_objects:
        binary = remove_small_objects(binary, small_object_size)
        if plots:
            plot_matrix(binary)

    log("Applying thinning algorithm")
    skel = thin(binary)
    if plots:
        plot_matrix(skel)

    searching = True
    jump = start_jump
    while searching:
        try:
            path = shortest_path(skel, intersects, direction, jump)
            searching = False
        except Exception as e:
            print(e)
            log("Failed to find path with jump value {}".format(jump))
            jump = jump + 5

    out = matrix.copy()
    for fp in path:
        out[fp[0], fp[1]] = 2
    if plots:
        plot_matrix(out)

    if out_file != "":
        with open(out_file, 'w') as f:
            json.dump(path, f, cls=NpEncoder)

    log("River trace complete.")
    return path
