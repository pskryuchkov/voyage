# Scrape instagram location list
# Run first

# Depencies: Chrome driver

from math import sin, cos, sqrt, radians, asin
from selenium.webdriver import Chrome, ChromeOptions
from random import randint, shuffle
from bs4 import BeautifulSoup
import json
import numpy as np
import warnings
import argparse
import sys
import time
import re
import os

from os import listdir
from os.path import isfile, join


def init_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", required=True, help="name of a city")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return vars(parser.parse_args())


def haversine(lon1, lat1, lon2, lat2):
    EARTH_RADIUS = 6373
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)

    try:
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        return EARTH_RADIUS * c
    except:
        return np.inf


def alphanum(str):
    pass1 = re.sub('[^\w+]', '_', str)
    pass2 = re.sub(r'[_]+','_', pass1)
    return pass2


SITE = "https://www.instagram.com"

args = init_arguments()
CITY = args['city']


JSON_PATH = 'locations_scraper.json'
with open(JSON_PATH, "r") as f:
    city_attributes = json.load(f)

COUNTRY_EXPLORE_LINK = city_attributes[CITY]['link']
COUNTRY_EXPLORE_PATH = join(SITE, COUNTRY_EXPLORE_LINK)
CITY_CENTER = city_attributes[CITY]['center']
MAX_DIST = city_attributes[CITY]['max_dist']

EXPLORE_LINK = "https://www.instagram.com/explore/locations/"

PROJECT_DIR = "../.."
LOCATION_DIR = join(PROJECT_DIR, "data/places_longlist/{}/".format(CITY))
# FIXME
UNRELEVANT_FILENAME = join(LOCATION_DIR, "unrelevant.txt".format(CITY))
# FIXME

LOCATIONS_PATH = join(LOCATION_DIR, "{}.txt")

N_PROBE = 10
TIMEOUT = 30

FLOAT_RE = "(\d+\.\d+)"

if not os.path.exists(LOCATION_DIR):
    os.makedirs(LOCATION_DIR)

options = ChromeOptions()
options.add_argument("headless")
driver = Chrome(chrome_options=options)
driver.set_page_load_timeout(TIMEOUT)
driver.implicitly_wait(TIMEOUT)

driver.get(COUNTRY_EXPLORE_PATH)

print("Expanding areas list...")
while True:
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #
        driver.find_element_by_css_selector("a[href*='{}?page=']".format(COUNTRY_EXPLORE_LINK)).click() #
        time.sleep(1)
    except:
        break

soup = BeautifulSoup(driver.page_source, "html.parser")
areas = [x['href'] for x in soup.find_all("a", href=re.compile("/explore/locations/c"))] #
print("NUMBER OF AREAS:", len(areas))

unrelevant_areas = ""
if os.path.isfile(UNRELEVANT_FILENAME):
    unrelevant_areas = "\n".join(open(UNRELEVANT_FILENAME, "r").readlines())

crawled_locations = list(map(lambda x: x.split(".")[0],
                             [f for f in listdir(LOCATION_DIR) if isfile(join("locations", f))]))

for area in areas:
    # FIXME
    area_name = area.split("/")[-2]

    if area_name in unrelevant_areas:
        continue

    driver.get(SITE + area)

    print("AREA: {}".format(area_name))
    probe_locations = re.findall('"id":"(\d+)"', driver.page_source)

    shuffle(probe_locations)

    dists = []
    for probe in probe_locations[:N_PROBE]:
        try:
            driver.get(EXPLORE_LINK + probe)
        except:
            continue

        re_lat = re.findall('"lat":' + FLOAT_RE, driver.page_source)  #
        re_lng = re.findall('"lng":' + FLOAT_RE, driver.page_source)  #
        if re_lat and re_lng:
            lat = float(re_lat[0]) 
            lng = float(re_lng[0])
        else:
            continue

        dists.append(round(haversine(CITY_CENTER[0], CITY_CENTER[1], lat, lng), 1))
        time.sleep(randint(1, 5))

    if (not dists) or np.nanmedian(dists) > MAX_DIST:
        print("NOT RELEVANT: {} km".format(round(np.median(dists), 1)))
        with open(UNRELEVANT_FILENAME, "a+") as f:
            f.write("{},{}\n".format(area_name, round(np.median(dists), 1)))
        continue

    driver.get(SITE + area)
    
    print("Expanding locations list...")
    while True:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  #
            driver.find_element_by_css_selector("a[href*='{}?page=']".format(area)).click()  #
            time.sleep(1)
        except:
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    locations_links = soup.find_all("a", href=re.compile("/explore/locations/[0-9]+"))  #
    print("NUMBER OF LOCATIONS:", len(locations_links))

    if locations_links:
        cache = []
        fn = LOCATIONS_PATH.format(area_name)
        if os.path.isfile(fn):
            cache = "\n".join(open(fn, "r").readlines())

        for j, link in enumerate(locations_links): 
            with open(fn, "a+") as report:   
                if link['href'] in cache:
                    print('already scanned: {}'.format(link['href']))
                    continue
                    
                try:
                    driver.get(SITE + link['href'])
                except:
                    print("GET error:", link)
                    continue

                re_cn = re.findall('"edge_location_to_media":{"count":(\d+)', driver.page_source)  #
                if re_cn:
                    cn = int(re_cn[0])
                else:
                    warnings.warn('Regexp error: {}'.format(link['href']), RuntimeWarning)
                    time.sleep(5)
                    continue

                label = alphanum(link.string)
                print("{}. {}".format(j+1, label))
                report.write('{},{},{}\n'.format(label, link['href'], cn))
    
driver.close()
