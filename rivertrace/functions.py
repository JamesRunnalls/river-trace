import heapq
import netCDF4
import numpy as np
import seaborn as sns
import networkx as nx
import geopandas as gp
from shapely.geometry import LineString, Point, shape
from datetime import datetime
from warnings import warn

import matplotlib.pyplot as plt
from matplotlib.path import Path


def log(text, indent=0):
    text = str(text).split(r"\n")
    for t in text:
        if t != "":
            out = datetime.now().strftime("%H:%M:%S.%f") + (" " * 3 * (indent + 1)) + t
            print(out)


def smooth(x, window_len=11, window='hanning'):
    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')
    y = np.convolve(w / w.sum(), s, mode='valid')
    return y


def get_pixel_values(path, matrix):
    v = []
    for i in range(len(path)):
        v.append(matrix[path[i][0], path[i][1]])
    return v


def find_index_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def plot_graph(path, file_out, mask):
    fig, ax = plt.subplots(len(file_out), 1, figsize=(18, 15))
    fig.subplots_adjust(hspace=0.5)
    x = range(len(path))
    for i in range(len(file_out)):
        matrix, lat, lon, mask = parse_netcdf(file_out[i]["file"], file_out[i]["variable"], mask=mask)
        y = get_pixel_values(path, matrix)
        ax[i].plot(x, y)
        ax[i].set_xlabel("Pixel Length")
        ax[i].set_ylabel(file_out[i]["variable"])
    plt.show()


def plot_matrix(matrix):
    fig, ax = plt.subplots(figsize=(18, 15))
    ax.imshow(matrix, interpolation='nearest')
    plt.tight_layout()
    plt.show()


def parse_netcdf(file, variable, mask=[]):
    log("Parsing NetCDF: "+file)
    nc = netCDF4.Dataset(file, mode='r', format='NETCDF4_CLASSIC')
    lat = np.array(nc.variables["lat"][:])
    lon = np.array(nc.variables["lon"][:])
    matrix = np.array(nc.variables[variable][:])
    if len(mask) == 0:
        mask = ~np.isnan(matrix).any(axis=1)
    matrix = matrix[mask]
    lat = lat[mask]
    return matrix, lat, lon, mask


def classify_water(matrix, threshold):
    log("Classify water pixels")
    binary = matrix.copy()
    binary[binary < threshold] = np.nan
    binary[~np.isnan(binary)] = True
    binary[np.isnan(binary)] = False
    return binary.astype(bool)


def get_intersections(lines):
    point_intersections = []
    line_intersections = []
    lines_len = len(lines)
    for i in range(lines_len):
        for j in range(i+1, lines_len):
            l1, l2 = lines[i], lines[j]
            if l1.intersects(l2):
                intersection = l1.intersection(l2)
                if isinstance(intersection, LineString):
                    line_intersections.append(intersection)
                elif isinstance(intersection, Point):
                    point_intersections.append(intersection)
                else:
                    raise Exception('What happened?')


def inside_matrix(point, lat, lon):
    return np.min(lon) < point.x < np.max(lon) and np.min(lat) < point.y < np.max(lat)


def classify_river(matrix, lat, lon, river, buffer=0.01):
    log("Classify water pixels as river or non river")
    r = gp.read_file(river)
    x, y = np.meshgrid(lon, lat)
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x, y)).T
    l1 = LineString([(np.min(lon), np.max(lat)), (np.max(lon), np.max(lat)), (np.max(lon), np.min(lat)), (np.min(lon), np.min(lat)), (np.min(lon), np.max(lat))])
    l2 = r["geometry"][0]
    it = l2.intersection(l1)
    if it.type == "GeometryCollection":
        s, e = l2.boundary
        x1 = find_index_nearest(lon, s.x)
        y1 = find_index_nearest(lat, s.y)
        x2 = find_index_nearest(lon, e.x)
        y2 = find_index_nearest(lat, e.y)
    if it.type == "Point":
        s, e = l2.boundary
        x1 = find_index_nearest(lon, it.x)
        y1 = find_index_nearest(lat, it.y)
        if inside_matrix(s, lat, lon):
            x2 = find_index_nearest(lon, s.x)
            y2 = find_index_nearest(lat, s.y)
        else:
            x2 = find_index_nearest(lon, e.x)
            y2 = find_index_nearest(lat, e.y)
    elif it.type == "MultiPoint":
        x1 = find_index_nearest(lon, it[0].x)
        y1 = find_index_nearest(lat, it[0].y)
        x2 = find_index_nearest(lon, it[1].x)
        y2 = find_index_nearest(lat, it[1].y)
    intersects = [[y1, x1], [y2, x2]]
    p = Path(r["geometry"][0].buffer(buffer).exterior.coords)
    grid = p.contains_points(points)
    mask = grid.reshape(len(lat), len(lon))
    matrix = matrix.copy()
    matrix[~mask] = False
    return matrix, intersects


def get_start_end_nodes(nodes, intersects, direction):
    nodes = np.asarray(nodes)
    dist_1 = np.sum((nodes - intersects[0]) ** 2, axis=1)
    dist_2 = np.sum((nodes - intersects[1]) ** 2, axis=1)
    node1 = nodes[np.argmin(dist_1)]
    node2 = nodes[np.argmin(dist_2)]
    if node1[0] > node2[0]:
        if direction == "N":
            start_node = "{}_{}".format(node1[0], node1[1])
            end_node = "{}_{}".format(node2[0], node2[1])
        elif direction == "S":
            start_node = "{}_{}".format(node2[0], node2[1])
            end_node = "{}_{}".format(node1[0], node1[1])
    elif node2[0] > node1[0]:
        if direction == "S":
            start_node = "{}_{}".format(node1[0], node1[1])
            end_node = "{}_{}".format(node2[0], node2[1])
        elif direction == "N":
            start_node = "{}_{}".format(node2[0], node2[1])
            end_node = "{}_{}".format(node1[0], node1[1])
    elif node1[1] > node2[1]:
        if direction == "W":
            start_node = "{}_{}".format(node1[0], node1[1])
            end_node = "{}_{}".format(node2[0], node2[1])
        elif direction == "E":
            start_node = "{}_{}".format(node2[0], node2[1])
            end_node = "{}_{}".format(node1[0], node1[1])
    elif node2[1] > node1[1]:
        if direction == "E":
            start_node = "{}_{}".format(node1[0], node1[1])
            end_node = "{}_{}".format(node2[0], node2[1])
        elif direction == "W":
            start_node = "{}_{}".format(node2[0], node2[1])
            end_node = "{}_{}".format(node1[0], node1[1])
    return start_node, end_node


def shortest_path(matrix, intersects, direction, jump):
    log("Calculating path from river skeleton with jump value {}".format(jump))
    river_pixels = np.where(matrix == 1)
    nodes = []
    edges = []
    G = nx.MultiGraph()
    for i in range(len(river_pixels[0])):
        if is_node(matrix, river_pixels[0][i], river_pixels[1][i]):
            nodes.append([river_pixels[0][i], river_pixels[1][i]])

    log("Found {} nodes, locating real edges.".format(len(nodes)), indent=1)
    for node in nodes:
        edges = get_real_edges(matrix, node, edges)

    log("Found {} real edges, locating jump edges.".format(len(edges)), indent=1)
    for node in nodes:
        edges = get_jump_edges(matrix, node, edges, jump=jump)

    log("Found {} total edges, calculating shortest path.".format(len(edges)), indent=1)
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=edge[2])

    start_node, end_node = get_start_end_nodes(nodes, intersects, direction)
    log("Identified start ({}) and end ({}) nodes".format(start_node, end_node), indent=1)

    path = nx.dijkstra_path(G, start_node, end_node)

    log("Exporting edges to path.", indent=1)
    full_path = []
    for i in range(1, len(path)):
        for edge in edges:
            if (path[i-1] == edge[0] or path[i] == edge[0]) and (path[i-1] == edge[1] or path[i] == edge[1]):
                p = edge[3]
                if len(p) > 0:
                    if "{}_{}".format(p[0][0], p[0][1]) != path[i-1]:
                        p.reverse()
                    p.pop(0)
                    full_path = full_path + p
                break
    return full_path


def get_real_edges(matrix, node, edges, max_iter=1000):
    ad = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
    yl, xl = matrix.shape
    for i in range(8):
        count = 0
        path = [node]
        search = True
        y = node[0]+ad[i][0]
        x = node[1]+ad[i][1]
        if x < 0 or x > xl - 1 or y < 0 or y > yl - 1:
            break
        if matrix[y, x]:
            prev = node
            curr = [y, x]
            path.append(curr)
            while search and count < max_iter:
                count += 1
                prev, curr, search = next_cell(matrix, prev, curr, yl, xl)
                path.append(curr)
                if count > max_iter-20:
                    print("Count: {}, node: {}".format(count, curr))
            if count >= max_iter:
                log("Iterations following path exceeded maximum allowed. Start node: {}".format(node), indent=2)
            else:
                start_end = ["{}_{}".format(node[0], node[1]), "{}_{}".format(curr[0], curr[1])]
                start_end.sort()
                edge = [start_end[0], start_end[1], count, path]
                if edge not in edges:
                    edges.append(edge)
    return edges


def get_jump_edges(matrix, node, edges, jump=10, jump_factor=1000):
    yl, xl = matrix.shape
    y = node[0]
    x = node[1]
    for i in range(max(y - jump, 0), min(yl, y + 1 + jump)):
        for j in range(max(x - jump, 0), min(xl, x + 1 + jump)):
            if not (i == y and j == x) and is_node(matrix, i, j):
                count = jump_factor * ((i-y)**2+(j-x)**2)**0.5
                start_end = ["{}_{}".format(y, x), "{}_{}".format(i, j)]
                start_end.sort()
                edge = [start_end[0], start_end[1], count, []]
                if edge not in edges:
                    edges.append(edge)
    return edges


def is_node(matrix, y, x):
    yl, xl = matrix.shape
    p_sum = np.sum(matrix[max(y-1, 0):min(yl, y+2), max(0, x-1):min(xl, x+2)])
    return matrix[y, x] == 1 and p_sum == 2 or p_sum > 3


def next_cell(matrix, prev, curr, yl, xl):
    ad = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
    pprev = prev
    y = curr[0]
    x = curr[1]
    if np.sum(matrix[max(y-1, 0):min(yl, y+2), max(0, x-1):min(xl, x+2)]) == 3:
        prev = curr
        for i in range(8):
            y_n = y + ad[i][0]
            x_n = x + ad[i][1]
            if x_n < 0 or x_n > xl - 1 or y_n < 0 or y_n > yl - 1:
                continue
            curr = [y_n, x_n]
            if matrix[y_n, x_n] and curr != prev and curr != pprev:
                break
        return prev, curr, True
    else:
        return prev, curr, False
