# v0.3

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
import urllib.request
import ssl
import re
from contextlib import contextmanager
from bs4 import BeautifulSoup
import urllib
import ssl
import os
import time
from random import randint
import datetime
import os.path


@contextmanager
def quiting(thing):
    try:
        yield thing
    finally:
        thing.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'q')
        thing.quit()


def download(url, fn):
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(url, context=context) as u:
            with open(fn, 'wb') as f:
                f.write(u.read())
    except:
        print("Download error!")

script_version="_spb"
float_pattern = "(\d+\.\d+)"
pic_size = 640
n_locations = 200

options = ChromeOptions()
options.add_argument("headless")

data = open("top_places.txt", "r").readlines()

locations_names = [x.split(",")[0] for x in data]
areas = [x.split(",")[1] for x in data]
locations_ids = [x.split(',')[2].strip() for x in data]

if not os.path.isfile("../photos{}/loc_info.csv".format(script_version)):
    with open("../photos{}/loc_info.csv".format(script_version), "w") as loc_info:
        loc_info.write("id,name,area,lat,lng,last_updated\n")

with quiting(Chrome(chrome_options=options)) as driver:
    driver.implicitly_wait(3)
    for j, loc in enumerate(locations_ids):
        start = time.time()

        area_name = areas[j]
        try:
            location_id = loc.split("/")[3]
        except:
            print("Invalid string: {}".format(data[j]))
            continue

        #saving_path = "../locations_photos/" + area_name + "/" + location_id
        saving_path = "../photos{}/{}/{}".format(script_version, area_name, location_id)

        if not os.path.exists(saving_path):
            os.makedirs(saving_path)
        else:
            print("already crawled:", loc)
            continue

        url = "https://www.instagram.com" + loc
        print(j+1, location_id)
        
        driver.get(url)

        for v in range(9):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.6)
            
        time.sleep(1)
        source = driver.page_source
        try:
            lat = float(re.findall('"lat":' + float_pattern, source)[0])
            lng = float(re.findall('"lng":' + float_pattern, source)[0])
            last_updated = sorted(re.findall('"taken_at_timestamp":(\d+)', source))[-1]
        except:
            print("Palimsya!")
            time.sleep(10)
            continue

        soup = BeautifulSoup(source, "html.parser")
        # "(https:\/\/[^,]*) 320w"
        links = soup.find_all("img", src=re.compile("https://instagram.+?{0}x{0}".format(pic_size)))

        if len(links) > 0:
            for g, x in enumerate(links):
                download(x['src'], "{}/{}.jpg".format(saving_path, g))

            with open("../photos{}/loc_info.csv".format(script_version), "a") as loc_info:
                loc_info.write("{},{},{},{},{},{}\n".format(location_id, re.sub('[^0-9a-zA-Zа-яёА-ЯЁ]+', '_', locations_names[j]), area_name, lat, lng, last_updated))
        else:
            print("Palimsya!")
            time.sleep(10)
            continue         

        time.sleep(randint(2, 5))

        print("time:", round(time.time() - start, 2))