# v0.2

import requests
from pprint import pprint
import json
import pandas as pd
import re
from bs4 import BeautifulSoup


def wiki_search(q, lang="ru"):
    url = "https://{}.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&utf8=&format=json".format(lang, q)
    response = requests.get(url)
    return json.loads(response.text)


def wiki_title(js):
    try:
        return js['query']['search'][0]['title']
    except:
        return None


def wiki_views(title, lang="ru"):
    url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{}.wikipedia/all-access/all-agents/{}/monthly/20170101/20180101"
    q = url.format(lang, title.replace(" ", "_"))
    response = requests.get(q)
    r = json.loads(response.text)
    if 'items' in r:
        return sum([x['views'] for x in r['items']])  
    else:
        return None


def is_relevant(article_title, keyword, lang="en"):
    url = "https://{}.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&rvsection=0&titles={}&format=json".format(lang, article_title)
    response = requests.get(url)
    if keyword in response.text.lower():
        return True
    else:
        return False

def article_coords(article_title, lang="en"):
    url = "https://{}.wikipedia.org/wiki/{}".format(lang, article_title.replace(" ", "_"))
    response = requests.get(url)
    try:
        return re.findall('"wgCoordinates":{"lat":(.*?),"lon":(.*?)}', response.text)[0]
    except:
        return None, None


def collect_articles(city, saving_interval=50):
    df = pd.read_csv("/Users/pavel/Sources/python/concepts/insta/scripts/top_places/top_places_{}.txt".format(city))
    locations = df.iloc[:, 0].tolist()

    data = []
    for j, x in enumerate(locations):
        #ru_str = re.sub("[a-zA-Z_]", " ", x).strip()
        en_str = re.sub("[а-яА-Я_]", " ", x).strip()

        ru_title, en_title = None, None

        #if ru_str:
        #    ru_title = wiki_title(wiki_search(ru_str, 'ru'))
        if en_str:
            en_title = wiki_title(wiki_search(en_str, 'en'))
        
        print("{}. {}, {}, {}".format(j+1, x, ru_title, en_title))
        data.append([x, ru_title, en_title])

        if j % saving_interval == 0 and j > 0:
            with open("wiki_{}.csv".format(city), "w") as file:
                for line in data:
                    loc, ru_title, en_title = line
                    file.write("{};{};{}\n".format(loc, ru_title, en_title))


def collect_views(city, keyword):
    df = pd.read_csv("/Users/pavel/Sources/python/concepts/insta/scripts/wiki/wiki_{}.csv".format(city), sep=";", header=None)
    df = df.drop_duplicates()

    name = df.iloc[:, 0].tolist()
    ru_locs = df.iloc[:, 1].tolist()
    en_locs = df.iloc[:, 2].tolist()

    data = []
    err_cn = 0
    for j in range(len(name)):
        en_sum = None

        if en_locs[j] != 'None' and is_relevant(en_locs[j], keyword):
            en_sum = wiki_views(en_locs[j], 'en')
            lat, lon = article_coords(en_locs[j])
            print("{}. {}, {}, {}, {}, {}".format(j+1, name[j], en_locs[j], lat, lon, en_sum))
            data.append([name[j], en_locs[j], lat, lon, en_sum])
        else:
            err_cn += 1

        if j % 50 == 0 and j > 0:
            with open("wiki_views_{}.csv".format(city), "w") as file:
                for line in data:
                    file.write("{};{};{};{};{}\n".format(*line))
    print(len(name), err_cn)


def polish(city):
    wiki_table = pd.read_csv("wiki_views_{}.csv".format(city), sep=";", header=None)
    wiki_table.columns = ["name", "wiki_name", "lon", "lat", "views"]

    wiki_table = wiki_table[wiki_table['views'] != 'None']
    wiki_table = wiki_table[wiki_table['lon'] != 'None']

    wiki_table = wiki_table[['wiki_name', 'lon', 'lat', 'views']].drop_duplicates()

    wiki_table.to_csv("wiki_items_{}.csv".format(city), index=False)


def try_parse(xml, tag):
    soup = BeautifulSoup(xml, "lxml")
    try:
        value = soup.find(tag).string
    except:
        value = None
    return value

"""
def wiki_geocoding(city):
    GEO_REQUEST = 'https://nominatim.openstreetmap.org/reverse?format=xml&lat={0}&lon={1}'
    wiki_table = pd.read_csv("wiki_items_{}.csv".format(city))

    wiki_suburbs, wiki_roads = [], []
    cn = 0
    for lat, lon in zip(wiki_table.lat, wiki_table.lon):
        response = requests.get(GEO_REQUEST.format(lon, lat))   

        suburb = try_parse(response.text, 'suburb')
        road = try_parse(response.text, 'road')       

        wiki_suburbs.append(suburb)
        wiki_roads.append(road)

        cn += 1
        print(cn, wiki_table.shape[0], suburb, road)

    wiki_table['suburb'] = wiki_suburbs
    wiki_table['roads'] = wiki_roads

    wiki_table.to_csv("wiki_located_items_{}.csv".format(city), index=False)
"""

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


def wiki_geocoding(city, language = 'en'):
    api_key = "AIzaSyCMoT57rB8xLg5Kba9NJ5BfPqH2GFWh_n0"
    GEO_REQUEST = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&key={2}&language={3}'
    
    wiki_table = pd.read_csv("wiki_items_{}.csv".format(city))

    wiki_roads = []
    cn = 0
    for lat, lon in zip(wiki_table.lat, wiki_table.lon):
        # FIXME: lon, lat
        response = requests.get(GEO_REQUEST.format(lon, lat, api_key, language))   

        geo_json = json.loads(response.text)
        # moscow sublocality_level_1
        # spb administrative_area_level_3
        # berlin sublocality_level_2
        # hong kong neighborhood
        # rome sublocality_level_1
        road, _ = get_address(geo_json, 'route', 'administrative_area_level_3')  

        wiki_roads.append(road)

        cn += 1
        print(cn, road, lon, lat)

    wiki_table['roads'] = wiki_roads

    wiki_table.to_csv("wiki_located_items_{}.csv".format(city), index=False)


CITY = "hong_kong" # "moscow"
CHECK_WORD = "hong kong" # "saint petersburg"

#collect_articles(CITY)
#collect_views(CITY, CHECK_WORD)
#polish(CITY)
wiki_geocoding(CITY)