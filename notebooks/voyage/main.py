import pickle

import numpy as np
import pandas as pd

import plotly.offline as py

from . import consts, streets, wiki, faces, scenes, clouds, data

pd.options.display.float_format = '{:.4g}'.format
py.init_notebook_mode(connected=True)


def get_settings(city, use_cache=False):
    def load_settings(city):
        nb_settings = data.load_json(consts.SETTINGS_FILE)

        class Settings:
            city_name = city
            city_center = nb_settings[city]['city_center']
            zoom = nb_settings[city]['zoom']
            language = nb_settings[city]['language']

            def __init__(self):
                pass

        return Settings

    if not hasattr(get_settings, '_settings'):
        get_settings._settings = load_settings(city)
    elif city != get_settings._settings.city_name or \
            not use_cache:
        get_settings._settings = load_settings(city)

    return get_settings._settings


def city_map(dataset):
    settings = get_settings(dataset.city)

    streets_table = streets.count_streets_location(dataset.geo_table)

    streets.draw_city_map(streets_table['longtitude'].tolist(),
                          streets_table['latitude'].tolist(),
                          streets_table[consts.STREET_KEY],
                          streets_table['counter'],
                          settings.city_center,
                          zoom=settings.zoom)


def street_area_combine(dataset):
    settings = get_settings(dataset.city)

    streets_list, street_activity, areas, area_activity = \
                                streets.count_activity(dataset.geo_table)

    streets_table = streets.count_streets_location(dataset.geo_table)

    streets_table_short = streets_table[:consts.N_STREETS_VISUALIZED]
    area_activity_short = area_activity[:consts.N_AREAS_VISUALIZED] + \
                                          [sum(area_activity[consts.N_AREAS_VISUALIZED + 1:])]
    areas_labels_short = areas[:consts.N_AREAS_VISUALIZED] + [consts.OTHER_LABEL]

    streets.draw_street_area_combine(streets_table_short[consts.STREET_KEY],
                                     streets_table_short['counter'],
                                     streets_table_short['latitude'],
                                     streets_table_short['longtitude'],
                                     area_activity_short,
                                     areas_labels_short,
                                     settings.language)


def insta_wiki_scatter(dataset):
    wiki_df = wiki.get_wiki_locations(dataset.wiki_table)

    if wiki_df.empty:
        return

    street_wiki_dict = wiki.get_street_wiki_views(wiki_df)

    street_insta_dict = wiki.get_insta_dict(dataset.top_places_table,
                                            dataset.geo_table)

    street_locs_wiki = wiki.get_street_locs(wiki_df)

    # FIXME: refactoring
    wiki_data = wiki.get_wiki_data(street_insta_dict,
                                   street_wiki_dict,
                                   street_locs_wiki)

    wiki.draw_insta_wiki_scatter([x[0] for x in wiki_data.values()],
                                 [x[1] for x in wiki_data.values()],
                                 [x[2] for x in wiki_data.values()])


def face_scatter(dataset):
    settings = get_settings(dataset.city)
    streets_table = streets.count_streets_location(dataset.geo_table)

    data_dict, street_locations = faces.process_face_data(dataset.loc_info,
                                                          dataset.face_data,
                                                          streets_table,
                                                          dataset.geo_table)

    faces.draw_face_scatter(data_dict, street_locations, settings.language)


def tags_rate(dataset):
    scenes_rates = scenes.selected_scenes_rates(dataset.photos_scenes)

    id2loc = scenes.get_id2loc(dataset.loc_info)
    hovers = scenes.get_rate_hover(dataset.photos_scenes, id2loc)

    bx, by = zip(*scenes_rates)

    bx = short_scene_labels(bx)

    scenes.draw_scenes_rate(bx, by, hovers)


def tags_delta(dataset, opposite_dataset):
    rates_delta = scenes.delta_scenes_rates(dataset.photos_scenes,
                                            opposite_dataset.photos_scenes)
    bx, by = zip(*rates_delta)

    bx = short_scene_labels(bx)

    scenes.draw_tags_delta(bx, by)


def short_scene_labels(scenes_list):
    return [x.split("/")[0] for x in scenes_list]


def streets_features(dataset):
    settings = get_settings(dataset.city)

    sorted_scenes = [x[0] for x in scenes.selected_scenes_rates(dataset.photos_scenes)]

    streets_list, _, _, _ = streets.count_activity(dataset.geo_table)

    if 'None' in streets_list:
        streets_list.remove('None')

    features_matrix = scenes.calculate_street_vectors(dataset.photos_scenes,
                                                      dataset.geo_table,
                                                      streets_list[:consts.N_STREETS],
                                                      sorted_scenes)

    scenes_labels = short_scene_labels(sorted_scenes)

    scenes.draw_streets_features(features_matrix, streets_list,
                                 scenes_labels, settings.language)


def tagged_city_map(dataset):
    streets_list, _, _, _ = streets.count_activity(dataset.geo_table)

    # FIXME: not obvious usage
    sorted_scenes = [x[0] for x in scenes.selected_scenes_rates(dataset.photos_scenes)]

    labels = [x.split("/")[0] for x in sorted_scenes]

    features_matrix = scenes.calculate_street_vectors(dataset.photos_scenes,
                                                      dataset.geo_table,
                                                      streets_list,
                                                      sorted_scenes)

    street2tag = scenes.get_top_streets_tags(features_matrix,
                                             streets_list,
                                             labels)

    streets_table = streets.count_streets_location(dataset.geo_table)

    settings = get_settings(dataset.city)

    tags_labels = []
    for x in streets_table[consts.STREET_KEY]:
        if x in street2tag:
            tag_value = street2tag[x][1]
            if np.isfinite(tag_value):
                tags_labels.append("{} {:.2f}".format(*street2tag[x]))
        else:
            pass

    scenes.draw_tagged_city_map(settings.city_center,
                                streets_table['longtitude'],
                                streets_table['latitude'],
                                streets_table['counter'],
                                tags_labels, settings.zoom)


def locations_scatter(dataset, opposite_dataset,
                      bro_threshold=0.68, use_cache=False):
    # TSNE
    ids, locations_features = scenes.get_locations_features(dataset.photos_scenes)
    opposite_ids, opposite_locations_features = scenes.get_locations_features(opposite_dataset.photos_scenes)

    joint_features = np.vstack((locations_features, opposite_locations_features))

    joint_ids = ids + opposite_ids

    if use_cache:
        print("Load t-SNE model from cache")
        with open('tsne.pickle', 'rb') as handle:
            planar_features = pickle.load(handle)
    else:
        planar_features = clouds.to_planar(joint_features)
        with open('tsne.pickle', 'wb') as handle:
            pickle.dump(planar_features, handle)

    # INDEXES_FILTERING
    id2city = {}
    id2city.update({x: dataset.city for x in ids})
    id2city.update({x: opposite_dataset.city for x in opposite_ids})

    indexes, opposite_indexes, other_indexes = \
            clouds.separate_indexes(dataset.city, opposite_dataset.city,
                                    planar_features, joint_ids, id2city,
                                    bro_threshold=bro_threshold)

    joint_indexes = indexes + opposite_indexes

    # HOVERS
    locations_scenes = scenes.get_locations_scenes(dataset.photos_scenes)
    opposite_locations_scenes = scenes.get_locations_scenes(opposite_dataset.photos_scenes)

    hovers = clouds.get_cloud_hovers(ids, dataset.loc_info,
                                     locations_scenes)

    opposite_hovers = clouds.get_cloud_hovers(opposite_ids, opposite_dataset.loc_info,
                                              opposite_locations_scenes)

    joint_hovers = np.array(hovers + opposite_hovers)

    labels, labels_coordinates = clouds.calc_labels_positions(locations_scenes,
                                                              opposite_locations_scenes,
                                                              joint_indexes,
                                                              planar_features)
    labels = np.array(labels)
    labels_coordinates = np.array(labels_coordinates)

    xp, yp = np.array(planar_features[0]), np.array(planar_features[1])

    showing_planar_x, showing_planar_y = xp[indexes], yp[indexes]
    opposite_showing_planar_x, opposite_showing_planar_y = \
        xp[opposite_indexes], yp[opposite_indexes]

    showing_hovers = joint_hovers[indexes]
    opposite_showing_hovers = joint_hovers[opposite_indexes]

    # CHECK ME
    clouds.draw_locations_scatter(showing_planar_x,
                                  showing_planar_y,
                                  opposite_showing_planar_x,
                                  opposite_showing_planar_y,
                                  showing_hovers,
                                  opposite_showing_hovers,
                                  labels,
                                  labels_coordinates,
                                  dataset.city,
                                  opposite_dataset.city)
