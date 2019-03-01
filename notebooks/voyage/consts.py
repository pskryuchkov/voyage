from os.path import join

# PATHS

PROJECT_PATH = "/Users/pavel/Sources/python/concepts/insta/"
PROJECT_PATH_NEW = '/Users/pavel/Sources/python/concepts/insta/public/'

TOP_PLACES_DIR = join(PROJECT_PATH, "scripts/top_places/")
TOP_PLACES_PATH = join(TOP_PLACES_DIR, "top_places_{}.txt")

PHOTOS_PATH = "public/photos/{}/"

LOCATIONS_FILE_DIR = join(PROJECT_PATH, PHOTOS_PATH)
LOCATIONS_FILE_PATH = join(LOCATIONS_FILE_DIR, "loc_info.csv")

ADRESSES_DIR = join(PROJECT_PATH_NEW, 'data/adresses/')
ADRESSES_PATH = join(ADRESSES_DIR, 'adresses_{}.csv')

SETTINGS_FILE = "notebooks_settings.json"

FACES_FILE_DIR = "/Users/pavel/Sources/python/concepts/insta/scripts/face_detect/faces/"
FACES_FILE_PATH = join(FACES_FILE_DIR, "faces_{}.json")

WIKI_FILE_DIR = "../../../scripts/wiki"
WIKI_FILE_PATH = join(WIKI_FILE_DIR, "wiki_located_items_{}.csv")

SCENES_PATH = join(PROJECT_PATH, "cv_sandbox/photo_tagger/scenes_{}.json")

# NOTEBOOK

TOKEN_FILE = "mapbox.token"
MAPBOX_TOKEN = open(TOKEN_FILE, "r").readlines()[0]

N_AREAS_VISUALIZED = 5
N_STREETS_VISUALIZED = 20
OTHER_LABEL = "Other"

TOP_AREAS_N = 10
TOP_STREETS_N = 100

N_SCENES = 25
SELECTED_TAGS = ['library/indoor', 'restaurant', 'street', 'bar',
                 'discotheque', 'promenade', 'museum/indoor', 'art_gallery',
                 'bridge', 'dressing_room', 'picnic_area', 'beer_hall',
                 'skyscraper', 'bookstore', 'closet', 'television_studio',
                 'stadium/soccer', 'pub/indoor', 'industrial_area', 'art_studio',
                 'lawn', 'highway', 'coffee_shop', 'booth/indoor', 'martial_arts_gym']

N_STREETS = 20
N_SKIP = 0
TOP_STREETS_VIS = 20
MAX_HOVER_LEN = 25

osm_area_key = 'area'
STREET_COLUMN = 'route'
