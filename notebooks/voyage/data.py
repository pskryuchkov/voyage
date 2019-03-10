import json

import pandas as pd

from . import consts, shared


def load_json(fn):
    with open(fn, "r") as f:
        return json.load(f)


class CityData:
    def __init__(self, city, load_all=True,
                 load_geo=False, load_scenes=False,
                 load_wiki=False, load_faces=False):
        self.city = city

        if load_all:
            self.geo_table = self.load_geo_table(city)
            self.photos_scenes = self.load_photos_scenes(city)
            self.wiki_table = self.load_wiki_table(city)
            self.face_data = self.load_face_data(city)
        else:
            if load_geo:
                self.geo_table = self.load_geo_table(city)
            if load_scenes:
                self.photos_scenes = self.load_photos_scenes(city)
            if load_wiki:
                self.wiki_table = self.load_wiki_table(city)
            if load_faces:
                self.face_data = self.load_face_data(city)

        self.top_places_table = self.load_top_places(city)
        self.loc_info = self.load_loc_info(city)


    def load_photos_scenes(self, city):
        scene_data = load_json(consts.SCENES_PATH.format(city))
        return scene_data

    def load_geo_table(self, city):
        geo_table = pd.read_csv(consts.ADDRESSES_PATH.format(city),
                                error_bad_lines=False, warn_bad_lines=False)

        geo_table = geo_table.drop_duplicates()

        geo_table[consts.STREET_KEY] = list(map(shared.title,
                                                geo_table[consts.STREET_KEY].tolist()))

        geo_table['longtitude'] = geo_table['longtitude'].astype(float)
        geo_table['latitude'] = geo_table['latitude'].astype(float)

        return geo_table

    def load_face_data(self, city):
        faces_json = load_json(consts.FACES_FILE_PATH.format(city))
        faces_json = {int(u): v for u, v in faces_json.items()}
        return faces_json

    def load_wiki_table(self, city):
        df = pd.read_csv(consts.WIKI_FILE_PATH.format(city),
                         error_bad_lines=False,
                         warn_bad_lines=False)
        return df

    def load_top_places(self, city):
        df = pd.read_csv(consts.TOP_PLACES_PATH.format(city),
                         header=None, warn_bad_lines=False)
        df.columns = ['name', 'area', 'link', 'photos_counter']
        return df

    def load_loc_info(self, city):
        loc_file = list(map(lambda x: x.strip().split(","),
                            open(consts.LOCATIONS_FILE_PATH.format(city), "r").readlines()[1:]))
        return loc_file

    def get_properties_dict(self):
        properties = {}
        properties['n_locations'] = len(self.photos_scenes)

        n_photos = 0
        for id in self.photos_scenes:
            n_photos += len(self.photos_scenes[id].keys())
        properties['n_photos'] = n_photos

        properties['n_streets'] = self.geo_table[consts.STREET_KEY].unique().size
        properties['n_areas'] = self.geo_table[consts.AREA_KEY].unique().size

        return properties
