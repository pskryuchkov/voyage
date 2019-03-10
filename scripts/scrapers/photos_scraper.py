# Scrape instagram locations photos
# Run after 'locations_rank.py'

# Depencies: Chrome driver

import os
from os.path import join, isfile, exists
import sys
import re
import time
import argparse
from random import randint
from contextlib import contextmanager

import urllib.request
import ssl

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup


def init_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", required=True, help="name of a city")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return vars(parser.parse_args())


def init_driver():

    @contextmanager
    def quiting(thing):
        try:
            yield thing
        finally:
            thing.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'q')
            thing.quit()

    options = ChromeOptions()
    options.add_argument("headless")
    return quiting(Chrome(chrome_options=options))


def download(url, fn):
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(url, context=context) as u:
            with open(fn, 'wb') as f:
                f.write(u.read())
    except:
        print("Download error!")


args = init_arguments()
city = args['city']

pic_size = 640
min_saved_photos = 5
skip_empty_paths = False

site = "https://www.instagram.com"
float_pattern = "(\d+\.\d+)"
name_filtering_pattern = '[^0-9a-zA-Zа-яёА-ЯЁ]+'

project_dir = "../.."
photo_dir = join(project_dir, "photos/{}".format(city))
top_locations_dir = join(project_dir, 'data/top_places')
top_locations_path = join(top_locations_dir, 'top_places_{}.txt'.format(city))
saved_locations_fn = "loc_info.csv"
saved_locations_path = join(photo_dir, saved_locations_fn) 

hush_interval = 10
n_down_scrolls = 10
scroll_interval = 0.6
preload_interval = 1
implicitly_wait_interval = 3

saved_locations_table_header = "id,name,area,lat,lng,last_updated\n"
saved_locations_row_template = "{},{},{},{},{},{}\n"

data = open(top_locations_path, "r").readlines()

locations_names = [x.split(",")[0] for x in data]
areas = [x.split(",")[1] for x in data]
locations_ids = [x.split(',')[2].strip() for x in data]

if not os.path.exists(photo_dir):
    os.makedirs(photo_dir)

if not isfile(saved_locations_path):
    with open(saved_locations_path, "w+") as loc_info:
        loc_info.write(saved_locations_table_header)

with init_driver() as driver:
    driver.implicitly_wait(implicitly_wait_interval)
    for j, loc in enumerate(locations_ids):
        start = time.time()

        area_name = areas[j]
        try:
            location_id = loc.split("/")[3]
        except:
            print("Invalid string: {}".format(data[j]))
            continue

        # FIXME
        location_photos_dir = join(photo_dir, area_name, location_id)

        if not exists(location_photos_dir):
            os.makedirs(location_photos_dir)
        else:
            if skip_empty_paths or len(os.listdir(location_photos_dir)) > min_saved_photos:
                print("Crawled:", loc)
                continue

        url = site + loc
        print(j+1, location_id)
        
        driver.get(url)

        for v in range(n_down_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_interval)
        
        source = driver.page_source
        try:
            lat = float(re.findall('"lat":' + float_pattern, source)[0])
            lng = float(re.findall('"lng":' + float_pattern, source)[0])
            last_updated = sorted(re.findall('"taken_at_timestamp":(\d+)', source))[-1]
        except:
            print("Page parsing error, sleeping...")
            time.sleep(hush_interval)
            continue

        soup = BeautifulSoup(source, "html.parser")
        links = [x['src'] for x in soup.find_all("img", 
                    src=re.compile("https://.+?{0}x{0}".format(pic_size)))]

        time.sleep(preload_interval)

        if len(links) > 0:
            for i, link in enumerate(links):
                download(link, join(location_photos_dir, "{}.jpg".format(i)))

            with open(saved_locations_path, "a") as loc_info:
                loc_info.write(saved_locations_row_template.format(location_id, 
                                re.sub(name_filtering_pattern, '_', locations_names[j]), 
                                area_name, lat, lng, last_updated))
        else:
            print("Download error, sleeping...")
            time.sleep(hush_interval)
            continue         

        time.sleep(randint(2, 5))

        print("Time:", round(time.time() - start, 2))