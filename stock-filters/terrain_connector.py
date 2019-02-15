import math
import os
import sys
from itertools import product, islice
import pickle
from subprocess import call, Popen, PIPE, STDOUT

import numpy as np
from utilityFunctions import setBlock


inputs = (
	("size", 256), # the material we want to use to build the mass of the structures
	)

COMPETITION_BOX = 256

input_file = "..\\GDMCcommunicationbucket\\terrain.pickle"
output_file = "..\\GDMCcommunicationbucket\\changes.pickle"

path_to_python = "C:\\Users\\Levi\\Code\\thesis\\terrain-analyzer\\venv\\Scripts\\python.exe"

def perform(level, box, options):
    COMPETITION_BOX = options["size"]
    x = int(math.floor((box.minx + box.maxx) / 2))
    y = int(math.floor((box.miny + box.maxy) / 2))
    z = int(math.floor((box.minz + box.maxz) / 2))
    half_size = int(COMPETITION_BOX / 2)

    print(box)

    terrain_inside_box = {}

    terrain = np.zeros((COMPETITION_BOX, COMPETITION_BOX, COMPETITION_BOX))

    count = 0
    for coord in product(*map(lambda e: range(int(e - half_size), int(e + half_size)), [x, y, z])):
        count += 1
        terrain[
            coord[0] - x + half_size, coord[1] - y + half_size, coord[2] - z + half_size] = level.blockAt(*coord)
        if count % 256 ** 2 == 0:
            print(count)

    os.chdir("..\\terrain-analyzer")

    with open(input_file, "wb") as f:
        pickle.dump({"box_size": {"x": COMPETITION_BOX, "y": COMPETITION_BOX, "z": COMPETITION_BOX},
                     "terrain": terrain}, f)

    print("exists: " + str(os.path.exists("gdmcconnector.py")))

    call([path_to_python, "gdmcconnector.py", input_file, output_file])

    logfile = open('logfile', 'w')
    proc = Popen([path_to_python, "gdmcconnector.py", input_file, output_file], stdout=PIPE, stderr=STDOUT)
    for line in proc.stdout:
        print(line)
        logfile.write(line)
    proc.wait()

    with open(output_file, "rb") as f:
        segments = pickle.load(f)

    # def convert_all_keys(dictionary, conversion_f):
    #     if type(dictionary) is dict:
    #         return dict((conversion_f(k), convert_all_keys(dictionary, conversion_f)) for k, v in dictionary.iteritems())
    #     else:
    #         return conversion_f(dictionary)
    #
    # segments = map(lambda segment: convert_all_keys(segment, lambda x: x.encode()), segments)

    os.chdir("../GDMC")

    for segment in segments:
        changed_voxels = segment[u"changed_voxels"]
        overlapping_voxels = segment[u"overlapping_voxels"]
        print "amount of changed voxels: " + str(len(changed_voxels))
        print "amount of overlapping voxels: " + str(len(overlapping_voxels))
        count = 1

        lowest = 9000, 9000, 9000
        highest = 0, 0, 0

        for changed_voxel in changed_voxels:
            current = (changed_voxel[u"x"], changed_voxel[u"y"],changed_voxel[u"z"])
            if reduce(lambda current, t: t[1] > highest[t[0]] and current,
                      enumerate(current), True):
                highest = current
            if reduce(lambda current, t: t[1] < lowest[t[0]] and current,
                      enumerate(current), True):
                lowest = current

        print(x - half_size, y - half_size, z - half_size)
        print "changed voxels"
        print "highest: " + str(highest)
        print "lowest: " + str(lowest)
        print "average_height: " + str(segment[u"average_height"])

        for changed_voxel in overlapping_voxels:
            current = (changed_voxel[u"x"], changed_voxel[u"y"],changed_voxel[u"z"])
            if reduce(lambda current, t: t[1] > highest[t[0]] and current,
                      enumerate(current), True):
                highest = current
            if reduce(lambda current, t: t[1] < lowest[t[0]] and current,
                      enumerate(current), True):
                lowest = current

        print(x - half_size, y - half_size, z - half_size)
        print "overlapping voxels"
        print "highest: " + str(highest)
        print "lowest: " + str(lowest)
        print "average_height: " + str(segment[u"average_height"])

        # lowest_with_adjustement = \
        #     lowest[0] + x - half_size,\
        #     lowest[1] + segment[u"average_height"] + (y - half_size),\
        #     lowest[2] + z - half_size
        #
        # highest_with_adjustement = \
        #     highest[0] + x - half_size, \
        #     highest[1] + segment[u"average_height"] + (y - half_size), \
        #     highest[2] + z - half_size
        #
        #
        # for empty_place in product(*map(lambda t: range(t[0], t[1])
        #         , zip(lowest_with_adjustement, highest_with_adjustement))):
        #     setBlock(level, (0, 0),
        #              *empty_place)

        for empty_place in overlapping_voxels:
        #     print((empty_place[0] + x - half_size,
        #              empty_place[1] + segment[u"average_height"] + (y - half_size),
        #              empty_place[2] + z - half_size))
            setBlock(level, (0, 0),
                     empty_place[u"x"] + x - half_size,
                     empty_place[u"y"] + segment[u"average_height"] + (y - half_size),
                     empty_place[u"z"] + z - half_size)

        print(x - half_size, y - half_size, z - half_size)
        print "highest: " + str(highest)
        print "lowest: " + str(lowest)
        print "average_height: " + str(segment[u"average_height"])

        for changed_voxel in changed_voxels:
            if not int(changed_voxel[u"value"]) == 0:
                setBlock(level,  (changed_voxel[u"value"], 0),
                         changed_voxel[u"x"] + x - half_size,
                         changed_voxel[u"y"] + segment[u"average_height"] + (y - half_size),
                         changed_voxel[u"z"] + z - half_size)
                count = count + 1
