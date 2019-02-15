import math
from itertools import product
from utilityFunctions import setBlock

from sklearn.cluster import KMeans
from utilityFunctions import setBlock
import numpy as np
import random
from sklearn.metrics.pairwise import euclidean_distances

COMPETITION_BOX = 90

x = 0
y = 1
z = 2

AIR = 0

"""
Get the competition terrain
"""
def perform(level, box, options):
    x = int(math.floor((box.minx + box.maxx)/ 2))
    y = int(math.floor((box.miny + box.maxy)/ 2))
    z = int(math.floor((box.minz + box.maxz)/ 2))
    half_size = int(COMPETITION_BOX/2)

    terrain_inside_box = {}

    for coord in product(*map(lambda e: range(int(e - half_size), int(e + half_size)), [x,y,z])):
        terrain_inside_box[coord[0] - x + half_size, coord[1] - y + half_size, coord[2] - z + half_size] = level.blockAt(*coord)
        # setBlock(level, (0, 0), *coord)

    class_1, class_2 = terrain_clustering_2d(level, terrain_inside_box, (COMPETITION_BOX, COMPETITION_BOX, COMPETITION_BOX))
    for e in class_1:
        setBlock(level, (9, 0), e[0] + x - half_size, e[1] + 1  + y - half_size, e[2] + z - half_size)
    for e in class_2:
        setBlock(level, (10, 0), e[0] + x - half_size, e[1] + 1  + y - half_size, e[2] + z - half_size)


"""
Get the competition terrain
"""
def get_terrain_on_top(terrain, coordinate_x_z, terrain_dimensions):
    current_height = terrain_dimensions[y] - 1
    current_terrain = terrain[coordinate_x_z[0], current_height, coordinate_x_z[1]]
    while current_terrain == AIR and current_height >= 0:
        current_height -= 1
        current_terrain = terrain[coordinate_x_z[0], current_height, coordinate_x_z[1]]
    return current_terrain, current_height

def euclidean_distance(X,Y):
    return sum(map(lambda p: (p[0] - p[1]) ** 2, zip(X, Y))) ** 0.5


def terrain_clustering_2d(level, terrain, terrain_dimensions=(256,256,256)):
    column_spaces = {}
    for column in product(*[range(0, terrain_dimensions[x]), range(0, terrain_dimensions[z])]):
        terrain_on_top, height = get_terrain_on_top(terrain, column, terrain_dimensions)
        column_spaces[column[0], column[1]] = {"x": column[0], "z": column[1], "h": height, "t": terrain_on_top}
    values = reduce(lambda agg, key: agg + [column_spaces[key]], column_spaces, [])
    random.shuffle(values)
    random_subset = values[0: (int(len(column_spaces.values())))]
    X = map(lambda c: map(int, [c["x"], c["z"], c["h"], c["t"]]), random_subset)
    kmeans = KMeans(n_clusters=2).fit(X)
    centers = list(map(lambda center: (center[0], center[1]), kmeans.cluster_centers_))
    class_1 = []
    class_2 = []
    for c in values:
        if euclidean_distances([[c["x"], c["z"]]], [[centers[0][0], centers[0][1]]]) < \
                euclidean_distances([[c["x"], c["z"]]], [[centers[1][0], centers[1][1]]]):
            class_1.append([c["x"], c["h"], c["z"]])
        else:
            class_2.append([c["x"], c["h"], c["z"]])
    return class_1, class_2
