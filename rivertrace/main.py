import os
import json
import numpy as np
from skimage.morphology import thin
from rivertrace.functions import log, shortest_path


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def check_inputs(matrix, start, end, save_path, include_gaps):
    if not isinstance(matrix, np.ndarray):
        raise ValueError("Input matrix must be a numpy array")
    if matrix.ndim != 2:
        raise ValueError("Input matrix must have two dimensions")
    if len(matrix[(matrix != 1) & (matrix != 0)]) != 0:
        raise ValueError("Input matrix must be binary")

    try:
        s_y = int(start[0])
        s_x = int(start[1])
    except:
        raise ValueError ("Unable to access start pixel co-ordinates")
    try:
        e_y = int(end[0])
        e_x = int(end[1])
    except:
        raise ValueError ("Unable to access start pixel co-ordinates")
    if not 0 <= s_y < matrix.shape[0]:
        raise ValueError("Start pixel y co-ordinate out of input matrix bounds")
    if not 0 <= s_x < matrix.shape[1]:
        raise ValueError("Start pixel x co-ordinate out of input matrix bounds")
    if not 0 <= e_y < matrix.shape[0]:
        raise ValueError("End pixel y co-ordinate out of input matrix bounds")
    if not 0 <= e_x < matrix.shape[1]:
        raise ValueError("End pixel x co-ordinate out of input matrix bounds")

    if not isinstance(save_path, str):
        raise ValueError("save_path must be a string")
    if not (os.path.isdir(os.path.dirname(save_path)) or save_path == ""):
        raise ValueError("save_path output folder does not exist")

    if not isinstance(include_gaps, bool):
        raise ValueError("include gaps must be a bool")


def trace(matrix, start, end, save_path="", include_gaps=True):
    """
        River tracing for satellite images.

        Parameters:
            matrix (np.array): 2D numpy binary array where 1 identifies river pixels
            start ([y, x]): Pixel coordinates for starting pixel
            end ([y, x]): Pixel coordinates for end pixel
            save_path (string): Path of output file, defaults no output
            include_gaps (bool): Include gaps between path sections in path
        Returns:
            path (list): An array of pixel locations that define the path.
        """

    check_inputs(matrix, start, end, save_path, include_gaps)

    log("Applying morphological thinning to binary matrix")
    skel = thin(matrix)

    log("Converting thinned map to nodes and edges and searching for shortest path")
    searching = True
    jump = 0
    while searching:
        try:
            path = shortest_path(skel, start, end, jump, include_gaps=include_gaps)
            searching = False
        except Exception as e:
            if "No path to" in str(e):
                log("Failed to find path with jump value {}".format(jump))
                jump = jump + 5
            else:
                raise
    log("River trace complete.")
    return path



