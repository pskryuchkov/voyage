# Locations coordinates reverse geocoding (by Google API)
# Run after 'photos_scraper.py'
# Depencies: Google API key

import requests
import csv
from os.path import isfile
import sys
import argparse
import json 

def init_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", required=True, help="name of the city")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return vars(parser.parse_args())


def save_csv(obj, fn, line_format, header=None, mode="w"):
    with open(fn, mode) as f:
        if header:
            f.write(header + "\n")
        for line in obj:
            f.write(line_format.format(*line))


def read_csv(fn, delimiter=','):
    obj = []
    with open(fn, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        for row in csv_reader:
            obj.append(row) 
    return obj


def get_address(google_api_response, street_key, area_key):
    street, area = None, None
    for result in google_api_response['results']:
        for component in result['address_components']:
            if not street and street_key in component['types']:
                if component['long_name'] != "Unnamed Road":
                    street = component['long_name']
            elif not area and area_key in component['types']:
                area = component['long_name']
    return street, area


def load_api_key():
    with open("google.token", "r") as f:
        data = f.readline()
    return data.strip()


def load_settings(city):
    with open("reverse_geocoding.json", "r") as f:
        data = json.load(f)
    return data[city]


args = init_arguments()
CITY = args['city']
PATH = "../../photos/{}/".format(CITY)
REQUEST_STR = "https://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&key={2}&language=ru"
ADDRESSES_FILENAME = "../../data/addresses/addresses_{}.csv".format(CITY)
SAVE_INTERVAL = 50

API_KEY = load_api_key()

STREET_KEY = 'route'
AREA_KEY = load_settings(CITY)

loc_file = list(map(lambda x: x.strip().split(","),
                    open(PATH + "loc_info.csv", "r").readlines()[1:]))

coordinates = []
for line in loc_file:
    id, name, area, lat, lng, modified = line
    coordinates.append((id, name, lat, lng))

cached = False
if isfile(ADDRESSES_FILENAME):
    addresses = read_csv(ADDRESSES_FILENAME)
    saved_locations = [x[1] for x in addresses]
    cached = True
else:
    addresses, saved_locations = [], []

for j, loc in enumerate(coordinates):

    error_flag = False

    id, name, lat, lng = loc
    
    if name in saved_locations:
        print("Skipping:", name)
        continue

    print(j+1, len(coordinates))

    r = requests.get(REQUEST_STR.format(lat, lng, API_KEY))

    geo_json = json.loads(r.text)

    route, area = get_address(geo_json, STREET_KEY, AREA_KEY)

    addresses.append([id, name, lat, lng, route, area])

    if (j % SAVE_INTERVAL == 0 and j > 0) or j == len(coordinates) - 1:
        line_format = ",".join(["{}"] * len(addresses[0])) + "\n"

        if not cached:
            header = "id,location,longtitude,latitude,route,area"
        else:
            header = None
            
        save_csv(addresses, ADDRESSES_FILENAME, line_format, header)
