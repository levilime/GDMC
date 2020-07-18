import math
import os
import sys
from itertools import product, islice
import pickle
from subprocess import call, Popen, PIPE, STDOUT

import numpy as np
from utilityFunctions import setBlock


inputs = (
	("name", "string"),
    ("minx", 0),
    ("miny", 0),
    ("minz", 0),
    ("maxx", 0),
    ("maxy", 0),
    ("maxz", 0)
	)

COMPETITION_BOX = 256
CENTRE_SELECTION = False
OPTION_SELECTION = False

path_to_python = "C:\\Users\\Levi\\Code\\thesis\\terrain-analyzer\\venv\\Scripts\\python.exe"

def input_output(name):
    return "C:\\Users\\Levi\\Code\\thesis\\GDMCcommunicationbucket\\terrain" + name + ".pickle", \
           "C:\\Users\\Levi\\Code\\thesis\\GDMCcommunicationbucket\\addtoterrain-" + name + ".pickle", \
           "C:\\Users\\Levi\\Code\\thesis\\GDMCcommunicationbucket\\removefromterrain-" + name + ".pickle"

def get_box_around_centre_of_selection(level, box):
    x = int(math.floor((box.minx + box.maxx) / 2))
    y = int(math.floor((box.miny + box.maxy) / 2))
    z = int(math.floor((box.minz + box.maxz) / 2))
    half_size = int(COMPETITION_BOX / 2)
    terrain = np.zeros((COMPETITION_BOX, COMPETITION_BOX, COMPETITION_BOX))

    count = 0
    for coord in product(*map(lambda e: range(int(e - half_size), int(e + half_size)), [x, y, z])):
        count += 1
        terrain[
            coord[0] - x + half_size, coord[1] - y + half_size, coord[2] - z + half_size] = level.blockAt(*coord)
        if count % 256 ** 2 == 0:
            print(count)
    return terrain

class MyBox:
    def __init__(self, minx, miny, minz, maxx, maxy, maxz):
        self.minx = minx
        self.miny = miny
        self.minz = minz
        self.maxx = maxx
        self.maxy = maxy
        self.maxz = maxz


def perform(level, default_box, options):
    box = None
    if OPTION_SELECTION:
        box = MyBox(options["minx"], options["miny"], options["minz"],
                    options["maxx"], options["maxy"], options["maxz"])
    if box is None:
        box = default_box
    if CENTRE_SELECTION:
        terrain = get_box_around_centre_of_selection(level, box)
        x = int(math.floor((box.minx + box.maxx) / 2))
        y = int(math.floor((box.miny + box.maxy) / 2))
        z = int(math.floor((box.minz + box.maxz) / 2))
        half_size = int(COMPETITION_BOX / 2)

        minx = x - half_size
        miny = y - half_size
        minz = z - half_size
    else:
        x = box.maxx - box.minx
        y = box.maxy - box.miny
        z = box.maxz - box.minz
        terrain = np.zeros((x, y, z), dtype=np.uint8)
        terrain_data_annotation = np.zeros((x, y, z), dtype=np.uint8)

        minx = box.minx
        miny = box.miny
        minz = box.minz

        count = 0
        for coord in product(*map(lambda t: range(t[0], t[1]),
                                  [(box.minx, box.maxx), (box.miny, box.maxy), (box.minz, box.maxz)])):
            count += 1
            terrain[
                coord[0] - box.minx, coord[1] - box.miny, coord[2] - box.minz] = level.blockAt(*coord)
            terrain_data_annotation[
                coord[0] - box.minx, coord[1] - box.miny, coord[2] - box.minz] = level.blockDataAt(*coord)
            if count % 256 ** 2 == 0:
                print(count)
    #


    os.chdir("C:\\Users\\Levi\\Code\\thesis\\terrain-analyzer")
    input_file = input_output(options["name"])[0]
    add_to_terrain_filename = input_output(options["name"])[1]
    remove_from_terrain_filename = input_output(options["name"])[2]
    with open(input_file, "wb") as f:
        pickle.dump({"box_size": {"x": COMPETITION_BOX, "y": COMPETITION_BOX, "z": COMPETITION_BOX},
                         "terrain": terrain, "terrain_data_annotation": terrain_data_annotation}, f)
    print("exists: " + str(os.path.exists("gdmcconnector.py")))

    call([path_to_python, "gdmcconnector.py", input_file, add_to_terrain_filename, remove_from_terrain_filename])

    with open(add_to_terrain_filename, "rb") as f:
        add_to_terrain = pickle.load(f)
    with open(remove_from_terrain_filename, "rb") as f:
        remove_from_terrain = pickle.load(f)

    # print(list(changes[(0,0,0)]))

    change_t = {23: 64,
     252: 1,
     246: 5,
     37: 20,
     192: 59,
     96: 3,
     6:50,
                17: 53}

    for t in remove_from_terrain:
        setBlock(level, (0, 0),
                 t[0] + box.minx,
                 t[1] + box.miny,
                 t[2] + box.minz
                 )

    for t in add_to_terrain:
        setBlock(level, (1, 0),
                 t[0] + box.minx,
                 t[1] + box.miny,
                 t[2] + box.minz
                 )

    # for index in changes:
    #     # remove, blocks, set blocks to air
    #     if changes[index][u's']:
    #         setBlock(level, (0, 0),
    #                          index[0] + box.minx,
    #                          index[1] + box.miny,
    #                          index[2] + box.minz
    #                 )
    #
    #     if not changes[index][u'a'] == 0:
    #
    #         # add blocks
    #         setBlock(level, (change_t[changes[index][u'a']] if changes[index][u'a'] in change_t else changes[index][u'a'], 0),
    #                  index[0] + box.minx,
    #                  index[1] + box.miny,
    #                  index[2] + box.minz
    #         )
    os.chdir("..\\..\\GDMC")

    #     addition_matrix = changes["addition_matrix"]
    #     addition_matrix_type = changes["addition_matrix_type"]
    #     substraction_matrix = changes["substraction_matrix"]
    #
    # it = np.nditer(addition_matrix, flags=['multi_index'])
    # while not it.finished:
    #     index = it.multi_index
    #     if substraction_matrix[index]:
    #         setBlock(level, (0, 0),
    #                  index[0] + box.minx,
    #                  index[1] + box.miny,
    #                  index[2] + box.minz
    #         )
    #     if not int(it[0]) == 0:
    #         setBlock(level, (int(it[0]), addition_matrix_type[it.multi_index]),
    #                  index[0] + box.minx,
    #                  index[1] + box.miny,
    #                  index[2] + box.minz
    #         )
    #     it.iternext()

