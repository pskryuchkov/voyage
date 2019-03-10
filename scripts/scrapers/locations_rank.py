# Sort locations by 'edge_location_to_media'
# Run after 'locations_scraper.py'

import sys
import argparse
from os import listdir
from os.path import isfile, join


def init_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", required=True, help="name of a city")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return vars(parser.parse_args())


args = init_arguments()
CITY = args['city']

N_LOCATIONS = 2000

PROJECT_DIR = "../.."
TARGET_PATH = join(PROJECT_DIR, "data/places_longlist/{}".format(CITY))
TOP_PLACES_PATH = join(PROJECT_DIR, "data/top_places/top_places_{}.txt".format(CITY))

data = []
for x in [f for f in listdir(TARGET_PATH) if isfile(join(TARGET_PATH, f))]:
    if isfile(join(TARGET_PATH, x)):
        lines = open(join(TARGET_PATH, x), "r", errors="ignore").readlines()
        area = x.split(".")[0]
        
        data += list(map(lambda z: "{},{}".format(area, z), lines))

# remove \n
data = [x.strip() for x in data]
data = [x.split(",") for x in data]

# check list len
data = filter(lambda x: len(x) == 4, data)

data = [[x[0], x[1], x[2], int(x[3])] for x in data if x[3].isdigit()]
data = sorted(data, key=lambda x: x[3], reverse=True)

with open(TOP_PLACES_PATH, "w") as f:
    for x in data[:N_LOCATIONS]:
        f.write("{},{},{},{}\n".format(x[1], x[0], x[2], x[3]))