from collections import Counter
from os.path import join as join
import operator
import json
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import warnings

import plotly.graph_objs as go
import plotly.offline as py

import voyage.consts as consts
import voyage.shared as shared
import voyage.styles as styles


def get_tags(mode, top_scenes=None):
    if mode == "top":
        return [x[0] for x in top_scenes]
    elif mode == "selected":
        return consts.SELECTED_TAGS


def tag_relevant_places(scene_data, tag, n_top=100):
    tag_values = {}
    for location in list(scene_data.keys()):
        value = 0
        for photo in scene_data[location]:
            photo_value = 0
            if tag in scene_data[location][photo]['categories']:
                photo_value = scene_data[location][photo]['categories'][tag]
            value += float(photo_value)
        if value > 0:
            tag_values[location] = value

    sorted_places = sorted(tag_values.items(),
                           key=operator.itemgetter(1),
                           reverse=True)[:n_top]

    return [x[0] for x in sorted_places]


def load_json(fn):
    with open(fn, "r") as f:
        return json.load(f)


def load_photos_scenes(city):
    fn = join(consts.PROJECT_PATH,
              consts.SCENES_PATH.format(city))
    scene_data = load_json(fn)
    return scene_data


def calc_scenes_rate(locations_scene_data):
    scenes_values = Counter()
    for loc in list(locations_scene_data.keys()):
        for photo in locations_scene_data[loc]:
            photo_scenes = locations_scene_data[loc][photo]['categories'].items()
            for category, val in photo_scenes:
                scenes_values[category] += float(val)
    return scenes_values


def get_id2loc(locations_data):
    return {x[0]: x[1] for x in locations_data}


def sort_matrix(m, row_idx, reverse=True):
    return sorted(m, key=lambda x: x[row_idx], reverse=reverse)


def normalize(ls):
    return [j / sum(ls) for j in ls]


def selected_scenes_rates(scene_data):
    scene_values = calc_scenes_rate(scene_data)

    selected_scenes_values = [scene_values[x] for x in consts.SELECTED_TAGS]
    normalized_scenes_values = normalize(selected_scenes_values)

    sorted_scenes = sort_matrix(zip(consts.SELECTED_TAGS,
                                    normalized_scenes_values), row_idx=1)
    return sorted_scenes


def get_rate_hover(scene_data, id2loc, n_places=5):
    top_scenes = selected_scenes_rates(scene_data)
    id_hovers = list([tag_relevant_places(scene_data, key, n_places)
                      for key, _ in top_scenes])

    name_hovers = []
    for location_hover in id_hovers:
        name_hovers.append([id2loc[x] for x in location_hover])

    printable_hovers = []
    for location_hover in name_hovers:
        printable_hovers.append("<br>".join(location_hover))

    return printable_hovers


def delta_scenes_rates(photos_scenes, opposite_photos_scenes):
    def list_to_dir(ls):
        return {u: v for u, v in ls}

    city_rates = list_to_dir(selected_scenes_rates(photos_scenes))
    opposite_city_rates = list_to_dir(selected_scenes_rates(opposite_photos_scenes))

    rates_delta = {}
    for key in city_rates:
        rates_delta[key] = city_rates[key] - opposite_city_rates[key]

    return sorted(rates_delta.items(), key=operator.itemgetter(1))


def draw_scenes_rate(bar_x, bar_y, hover_text):
    style = styles.TagsRateStyle

    trace = go.Bar(x=bar_x, y=bar_y,
                   opacity=style.OPACITY,
                   marker=dict(color=style.RATE_BAR_COLOR),
                   text=hover_text, hoverinfo="y+text")

    yaxis_style = dict(tickfont=dict(size=style.FONT_SIZE,
                                     color=style.TICKFONT_COLOR))
    xaxis_style = dict(tickfont=dict(size=style.FONT_SIZE,
                                     color=style.TICKFONT_COLOR),
                       tickangle=-90)

    layout = go.Layout(height=style.PLOT_HEIGHT,
                       width=style.PLOT_WIDTH,
                       xaxis1=xaxis_style, xaxis2=xaxis_style,
                       yaxis1=yaxis_style, yaxis2=yaxis_style,
                       margin=style.MARGIN, showlegend=False)

    fig = dict(data=[trace], layout=layout)
    py.iplot(fig, show_link=False)


def draw_tags_delta(delta_bar_x, delta_bar_y):
    style = styles.TagsDeltaStyle

    trace = go.Bar(x=delta_bar_x,
                   y=delta_bar_y, opacity=style.OPACITY,
                   marker=dict(color=style.DELTA_BAR_COLOR))

    yaxis_style = dict(tickfont=dict(size=style.FONT_SIZE,
                                     color=style.TICKFONT_COLOR))
    xaxis_style = dict(tickfont=dict(size=style.FONT_SIZE,
                                     color=style.TICKFONT_COLOR),
                       tickangle=-90)

    layout = go.Layout(height=style.PLOT_HEIGHT,
                       width=style.PLOT_WIDTH,
                       xaxis1=xaxis_style, xaxis2=xaxis_style,
                       yaxis1=yaxis_style, yaxis2=yaxis_style,
                       margin=style.MARGIN, showlegend=False)

    fig = dict(data=[trace], layout=layout)
    py.iplot(fig, show_link=False)


def get_locations_scenes(photos_scenes):
    locations_scenes = {}
    for location_id in photos_scenes:

        accumulated_scenes_values = Counter()
        for photo in photos_scenes[location_id]:
            for category, value in photos_scenes[location_id][photo]['categories'].items():
                accumulated_scenes_values[category] += float(value)

        locations_scenes[location_id] = accumulated_scenes_values

    raw_scenes_table = []
    for location_id in locations_scenes:
        selected_scenes = [locations_scenes[location_id][tag] for tag in consts.SELECTED_TAGS]
        table_line = [location_id] + selected_scenes
        raw_scenes_table.append(table_line)

    columns = ["id"] + consts.SELECTED_TAGS
    return pd.DataFrame(raw_scenes_table, columns=columns)


def calculate_street_vectors(scene_data, geo_table,
                             streets_list, sorted_tags):
    scenes_table = get_locations_scenes(scene_data)

    street_vectors = []
    for street in streets_list:
        accumulated_vector = np.zeros(consts.N_SCENES)
        locations_id = geo_table[geo_table[consts.STREET_KEY] == street]\
                                ['id'].astype(str)
        for loc in locations_id:
            if loc in scenes_table.id.values:
                is_relevant_row = (scenes_table['id'] == loc)
                relevant_row = scenes_table[is_relevant_row][sorted_tags]

                location_vector = relevant_row.iloc[0].tolist()
                accumulated_vector += location_vector

        street_vectors.append(accumulated_vector)

    return np.array(street_vectors)


def draw_streets_features(features_matrix, street_labels,
                          tag_labels, language):

    style = styles.StreetsFeaturesPlotStyle

    plt.figure(figsize=(style.PLT_WIDTH,
                        style.PLT_HEIGHT))

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [style.MIN_VALUE_COLOR,
                                                                    style.MAX_VALUE_COLOR])

    plt.imshow(features_matrix, cmap=cmap, vmax=style.MAX_IM_VALUE)

    ax = plt.gca()
    ax.set_xticks(np.arange(-0.5, consts.N_SCENES, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, consts.TOP_STREETS_VIS, 1), minor=True)

    ax.tick_params(width=0)
    ax.tick_params(which="minor", width=0)

    for side in ['top', 'right', 'bottom', 'left']:
        ax.spines[side].set_visible(False)

    plt.grid(which="minor",
             color=style.GRID_COLOR,
             linestyle='-',
             linewidth=style.GRID_WIDTH)

    if re.findall(style.CHINESE_RE, " ".join(street_labels)):
        warnings.warn("Chinese characters will be hide because of bad matplotlib support")
        street_labels = [re.sub(style.CHINESE_RE, '', x).strip() for x in street_labels]

    if language == 'ru':
        street_labels = list(map(shared.street_normalize_ru, street_labels))

    plt.xticks(range(consts.N_SCENES),
               tag_labels,
               rotation=style.XTICKS_ROTATION,
               size=style.FONT_SIZE,
               color=style.LABEL_COLOR)

    plt.yticks(range(consts.TOP_STREETS_VIS),
               street_labels,
               size=style.FONT_SIZE,
               color=style.LABEL_COLOR)


def get_top_streets_tags(street_vectors, map_streets, labels):
    street_tags = {}
    for u, v in zip(map_streets, street_vectors):
        sort = sorted(list(zip(labels[1:], v[1:])),
                      key=lambda x: x[1], reverse=True)
        top = sort[0]
        val_sum = sum([x[1] for x in sort])

        if val_sum:
            norm_val_sum = top[1] / val_sum
        else:
            norm_val_sum = 0

        street_tags[u] = [top[0], norm_val_sum]

    return street_tags


def get_locations_features(photos_scenes):
    locations_scenes = get_locations_scenes(photos_scenes)
    return locations_scenes['id'].values.tolist(), \
           locations_scenes[consts.SELECTED_TAGS].values.tolist()


def draw_tagged_city_map(city_center, lat, lon, streets_locations_number, tags_labels):
    style = styles.TaggedCityMapStyle

    tags_labels = [x if streets_locations_number.iloc[j] > style.MIN_LOCATIONS
                   else "" for j, x in enumerate(tags_labels)]

    marker_sizes = [x if x < style.MAX_MARKER_SIZE else style.MAX_MARKER_SIZE
                    for x in streets_locations_number]
    marker_sizes = [x if x > style.MIN_MARKER_SIZE else style.MIN_MARKER_SIZE
                    for x in marker_sizes]

    data = [go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers+text',
        marker=dict(
            size=marker_sizes,
            color=style.MARKER_COLOR,
            opacity=style.MARKER_OPACITY),
        text=tags_labels,
        textfont=dict(size=style.FONT_SIZE, color=style.FONT_COLOR),
        hoverinfo='none'
    )]

    layout = go.Layout(
        width=style.MAP_WIDTH,
        height=style.MAP_HEIGHT,
        hovermode='closest',
        margin=style.MARGIN,
        mapbox=dict(
            accesstoken=consts.MAPBOX_TOKEN,
            center=dict(
                lat=city_center[0],
                lon=city_center[1]),
            zoom=style.ZOOM,
            style='light'
        ))

    fig = dict(data=data, layout=layout)
    py.iplot(fig, show_link=False)
