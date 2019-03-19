from os.path import join

# PATHS

PROJECT_PATH = ".."

TOP_PLACES_DIR = join(PROJECT_PATH, "data/top_places")
TOP_PLACES_PATH = join(TOP_PLACES_DIR, "top_places_{}.txt")

PHOTOS_PATH = "photos/{}/"

LOCATIONS_FILE_DIR = join(PROJECT_PATH, PHOTOS_PATH)
LOCATIONS_FILE_PATH = join(LOCATIONS_FILE_DIR, "loc_info.csv")

ADDRESSES_DIR = join(PROJECT_PATH, 'data/addresses')
ADDRESSES_PATH = join(ADDRESSES_DIR, 'addresses_{}.csv')

SETTINGS_FILE = "notebooks_settings.json"

FACES_FILE_DIR = join(PROJECT_PATH, "data/faces")
FACES_FILE_PATH = join(FACES_FILE_DIR, "faces_{}.json")

WIKI_FILE_DIR = join(PROJECT_PATH, "data/wiki")
WIKI_FILE_PATH = join(WIKI_FILE_DIR, "wiki_located_items_{}.csv")

SCENES_DIR = join(PROJECT_PATH, "data/scenes")
SCENES_PATH = join(SCENES_DIR, "scenes_{}.json")

# NOTEBOOK

TOKEN_FILE = "mapbox.token"
MAPBOX_TOKEN = open(TOKEN_FILE, "r").readlines()[0]

N_AREAS_VISUALIZED = 5
N_STREETS_VISUALIZED = 20
OTHER_LABEL = "Other"

TOP_AREAS_N = 10
TOP_STREETS_N = 100

SELECTED_TAGS = ['library/indoor', 'restaurant', 'street', 'bar',
                 'discotheque', 'promenade', 'museum/indoor', 'art_gallery',
                 'bridge', 'dressing_room', 'picnic_area', 'beer_hall',
                 'skyscraper', 'bookstore', 'closet', 'television_studio',
                 'stadium/soccer', 'pub/indoor', 'industrial_area', 'art_studio',
                 'lawn', 'highway', 'coffee_shop', 'booth/indoor', 'martial_arts_gym',
                 'church/indoor', 'fountain', 'delicatessen', 'florist_shop/indoor', 'sushi_bar']

N_SCENES = len(SELECTED_TAGS)

N_STREETS = 20
N_SKIP = 0
TOP_STREETS_VIS = 20
MAX_HOVER_LEN = 25

AREA_KEY = 'area'
STREET_KEY = 'route'
