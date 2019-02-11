# v0.3

from math import sin, cos, sqrt, atan2, radians, asin
from selenium.webdriver import Chrome, ChromeOptions
from random import randint, shuffle
from bs4 import BeautifulSoup
import numpy as np
import warnings
import time
import re
import os

from os import listdir
from os.path import isfile, join


# center = [59.9384, 30.3158] # palace square
#center = [52.523695, 13.417237] # alexanderplatz
# center = [55.7535, 37.62] # red square
#center = [41.393011, 2.161416] # barcelona
#center = [22.257328, 114.198523] # hong kong 
center = [41.902689, 12.496176] # rome

# max_dist = 30 # moscow
#max_dist = 20 # spb
#max_dist = 20 # berlin
#max_dist = 7 # barcelona
#max_dist = 9 # hong kong
max_dist = 15

def haversine(lon1, lat1, lon2, lat2):
    R = 6373
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)

    try:
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        return R * c
    except:
        return np.inf


def alphanum(str):
    pass1 = re.sub('[^\w+]', '_', str)
    pass2 = re.sub(r'[_]+','_', pass1)
    return pass2


insta_loc = "https://www.instagram.com/explore/locations/" #
site = "https://www.instagram.com"

unrelevant_fn = "locations/unrelevant.txt"
loc_fn = "locations/{}.txt"

float_pattern = "(\d+\.\d+)"

n_probe = 10

options = ChromeOptions()
options.add_argument("headless")
driver = Chrome(chrome_options=options)
driver.set_page_load_timeout(30)
driver.implicitly_wait(30)

#driver.get("https://www.instagram.com/explore/locations/RU/russia/") #
#driver.get("https://www.instagram.com/explore/locations/DE/germany/")
#driver.get("https://www.instagram.com/explore/locations/ES/spain/")
#driver.get("https://www.instagram.com/explore/locations/HK/hong-kong/")
driver.get("https://www.instagram.com/explore/locations/IT/italy/")

print("Expanding areas list...")
while True:
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #
        driver.find_element_by_css_selector("a[href*='explore/locations/RU/russia/?page=']").click() #
        time.sleep(1)
    except:
        break

soup = BeautifulSoup(driver.page_source, "html.parser")
areas = [x['href'] for x in soup.find_all("a", href=re.compile("/explore/locations/c"))] #
print("NUMBER OF AREAS:", len(areas))

unrelevant_areas = ""
if os.path.isfile(unrelevant_fn):
    unrelevant_areas = "\n".join(open(unrelevant_fn, "r").readlines())

crawled_locations = list(map(lambda x: x.split(".")[0], [f for f in listdir("locations") if isfile(join("locations", f))]))

for area in areas:
    area_name = area.split("/")[-2]  #

    #if area_name in crawled_locations:
    #    continue
    if area_name in unrelevant_areas:
        continue

    driver.get(site + area)

    print("AREA: {}".format(area_name))
    probe_locations = re.findall('"id":"(\d+)"', driver.page_source)

    shuffle(probe_locations)

    dists = []
    for probe in probe_locations[:n_probe]:
        try:
            driver.get(insta_loc + probe)
        except:
            continue

        re_lat = re.findall('"lat":' + float_pattern, driver.page_source)  #
        re_lng = re.findall('"lng":' + float_pattern, driver.page_source)  #
        if re_lat and re_lng:
            lat = float(re_lat[0]) 
            lng = float(re_lng[0])
        else:
            continue

        dists.append(round(haversine(center[0], center[1], lat, lng), 1))
        time.sleep(randint(1, 5))

    if (not dists) or np.nanmedian(dists) > max_dist:
        print("NOT RELEVANT: {} km".format(round(np.median(dists), 1)))
        with open(unrelevant_fn, "a+") as f:
            f.write("{},{}\n".format(area_name, round(np.median(dists), 1)))
        continue

    driver.get(site + area)
    
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
        fn = loc_fn.format(area_name)
        if os.path.isfile(fn):
            cache = "\n".join(open(fn, "r").readlines())

        for j, link in enumerate(locations_links): 
            with open(fn, "a+") as report:   
                if link['href'] in cache:
                    print('already scanned: {}'.format(link['href']))
                    continue
                    
                try:
                    driver.get(site + link['href'])
                except:
                    print("GET error:", link)
                    continue

                re_cn = re.findall('"edge_location_to_media":{"count":(\d+)', driver.page_source)  #
                if re_cn:
                    cn = int(re_cn[0])
                else:
                    warnings.warn('Regexp error: {}'.format(link['href']), RuntimeWarning)
                    continue

                label = alphanum(link.string)
                print("{}. {}".format(j+1, label))
                report.write('{},{},{}\n'.format(label, link['href'], cn))
    
driver.close()