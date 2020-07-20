import math
import os
from itertools import product
import pickle
from subprocess import call

import numpy as np
from utilityFunctions import setBlock


inputs = (
	("name", "string"),
    ("path", "string"),
    ("pathtopython3", "string"),
    ("solvingtimeinseconds","string")
	)

COMPETITION_BOX = 256
CENTRE_SELECTION = False
OPTION_SELECTION = False

 # "C:\\Users\\Levi\\Code\\thesis\\terrain-analyzer\\venv\\Scripts\\python.exe"
# C:\\Users\\Levi\\Code\\thesis\\GDMCcommunicationbucket
def input_output(name, path):
    return path +"\\terrain" + name + ".pickle", \
           path + "\\addtoterrain-" + name + ".pickle", \
           path + "\\removefromterrain-" + name + ".pickle"

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


def obtain_terrain(level, box, default_box):
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
    return terrain

def perform(level, default_box, options):
    path_to_python = options["pathtopython3"]
    current_path = os.getcwd()
    box = None
    if box is None:
        box = default_box
    if OPTION_SELECTION:
        box = MyBox(options["minx"], options["miny"], options["minz"],
                    options["maxx"], options["maxy"], options["maxz"])


    os.chdir("C:\\Users\\Levi\\Code\\thesis\\terrain-analyzer")
    input_file = input_output(options["name"], options["path"])[0]
    add_to_terrain_filename = input_output(options["name"], options["path"])[1]
    remove_from_terrain_filename = input_output(options["name"], options["path"])[2]
    solving_time = options["solvingtimeinseconds"] if options["solvingtimeinseconds"] else 600


    terrain = obtain_terrain(level, box, default_box)
    with open(input_file, "wb") as f:
        pickle.dump({"box_size": {"x": box.maxx - box.minx, "y": box.maxy - box.miny, "z": box.maxz - box.minz},
                         "terrain": terrain, "terrain_data_annotation": {}}, f)
    print("exists: " + str(os.path.exists("gdmcconnector.py")))
    call([path_to_python, "gdmcconnector.py", input_file, add_to_terrain_filename, remove_from_terrain_filename, solving_time])

    # with open(add_to_terrain_filename, "rb") as f:
    #     add_to_terrain = pickle.load(f)
    # with open(remove_from_terrain_filename, "rb") as f:
    #     remove_from_terrain = pickle.load(f)

    add_to_terrain = read_csv_tuple_list(add_to_terrain_filename)
    remove_from_terrain = read_csv_tuple_list(remove_from_terrain_filename)

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

    current_material = 1
    for t in add_to_terrain:
        if t[3] == 67 or t[3] == 68 or t[3] == 69 or t[3] == 70:
            setBlock(level, (53, t[3] % 67),
                     t[0] + box.minx,
                     t[1] + box.miny,
                     t[2] + box.minz
                     )
        elif t[3] == 45 or t[3] == 46 or t[3] == 47:
            setBlock(level, (44, t[3] % 44),
                     t[0] + box.minx,
                     t[1] + box.miny,
                     t[2] + box.minz
                     )
        elif t[3] == 131:
            setBlock(level, (193, 0),
                     t[0] + box.minx,
                     t[1] + box.miny,
                     t[2] + box.minz
                     )
            setBlock(level, (193, 8),
                     t[0] + box.minx,
                     t[1] + box.miny + 1,
                     t[2] + box.minz
                     )
        elif t[3] == 111:
            setBlock(level, (45, 0),
                     t[0] + box.minx,
                     t[1] + box.miny ,
                     t[2] + box.minz
                     )
        elif t[3] == 112:
            setBlock(level, (43, 0),
                     t[0] + box.minx,
                     t[1] + box.miny,
                     t[2] + box.minz
                     )
        elif t[3] == 216:
            setBlock(level, (50, 5),
                     t[0] + box.minx,
                     t[1] + box.miny,
                     t[2] + box.minz
                     )
        elif t[3] == 9 or t[3] == 246:
            setBlock(level, (current_material, 0),
                     t[0] + box.minx,
                     t[1] + box.miny,
                     t[2] + box.minz
                     )
        else:
            current_material = t[3]
            setBlock(level, (t[3], 0),
                     t[0] + box.minx,
                     t[1] + box.miny,
                     t[2] + box.minz
                     )
    os.chdir(current_path)

def read_csv_tuple_list(location):
    f = open(location, "r")
    return map(lambda t: tuple(map(int, t.split(","))), f.readlines())
