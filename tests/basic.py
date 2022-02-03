import numpy as np
from rivertrace import trace
from rivertrace.functions import plot_matrix

square = np.zeros((20, 20), dtype=np.uint8)
square[0:2, 0:5] = 1
square[0:8, 5:8] = 1
square[6:9, 8:12] = 1
square[8:15, 10:14] = 1
square[15:20, 12:15] = 1
square[18:20, 15:20] = 1

path = trace(square, [0, 0], [19, 19])

for p in path:
    square[p[0], p[1]] = 2

plot_matrix(square, "Final path plotted on original data")

