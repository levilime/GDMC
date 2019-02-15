import math
from itertools import product
import pickle
import numpy as np


inputs = (
	("size", 256), # the material we want to use to build the mass of the structures
	)

COMPETITION_BOX = 256

def perform(level, box, options):
    COMPETITION_BOX = options["size"]
    x = int(math.floor((box.minx + box.maxx) / 2))
    y = int(math.floor((box.miny + box.maxy) / 2))
    z = int(math.floor((box.minz + box.maxz) / 2))
    half_size = int(COMPETITION_BOX / 2)

    terrain_inside_box = {}

    terrain = np.zeros((COMPETITION_BOX, COMPETITION_BOX, COMPETITION_BOX))

    count = 0
    for coord in product(*map(lambda e: range(int(e - half_size), int(e + half_size)), [x, y, z])):
        count += 1
        terrain[
            coord[0] - x + half_size, coord[1] - y + half_size, coord[2] - z + half_size] = level.blockAt(*coord)
        # if level.blockAt(*coord) == 17:
        #     print(level.blockAt(*coord))
            # terrain_inside_box[
        #     coord[0] - x + half_size, coord[1] - y + half_size, coord[2] - z + half_size] = level.blockAt(*coord)
        if count % 256 ** 2 == 0:
            print(count)

    with open("output_terrain.pickle", "wb") as f:
        pickle.dump({"box_size": {"x": COMPETITION_BOX, "y": COMPETITION_BOX, "z": COMPETITION_BOX},
                     "terrain": terrain}, f)