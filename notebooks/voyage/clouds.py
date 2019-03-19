import sys

import numpy as np

from sklearn.manifold import TSNE

import plotly.graph_objs as go
import plotly.offline as py

from . import consts, scenes, shared, styles

MAX_INT = sys.maxsize


def to_planar(features_table):
    planar_features = TSNE().fit_transform(features_table).T

    return planar_features


def short_tag(x):
    return x.split("/")[0]


def location_tags(features, n_top=3):
    top_idx = np.argsort(features[consts.SELECTED_TAGS].tolist())[-n_top:][::-1]
    top_tags = [short_tag(consts.SELECTED_TAGS[x]) for x in top_idx]
    return top_tags


def get_cloud_hovers(ids, locations_data, photos_scenes):
    id2loc_target = scenes.get_id2loc(locations_data)

    id2tags = {}
    for index, row in photos_scenes.iterrows():
        id2tags[row['id']] = location_tags(row)

    hovers = ["{}<br>{}".format(shared.trim(id2loc_target[x].replace("_", " ")),
                                ", ".join(id2tags[x]))
              if x in id2loc_target else "_"
              for x in ids]

    return hovers


def separate_indexes(city, opposite_city,
                     points, ordered_ids, id2city,
                     n_neighbors=10, bro_threshold=0.7):

    def sort_by_dist(node, nodes):
        dist_2 = np.sum((np.asarray(nodes) - node) ** 2, axis=1)
        return np.argsort(dist_2)

    visual_data_list = list(points.T)

    n_points = len(ordered_ids)
    indexes, opposite_indexes, other_indexes = [], [], []
    for j in range(n_points):
        point = points[0, j], points[1, j]
        other_points = visual_data_list[:j] + visual_data_list[j + 1:]

        closest_locations = sort_by_dist(point, other_points)[:n_neighbors]

        curr_city = id2city[ordered_ids[j]]
        closest_locations_cities = [id2city[ordered_ids[x]] for x in closest_locations]

        if closest_locations_cities.count(curr_city) / \
                len(closest_locations_cities) > bro_threshold:
            if curr_city == city:
                indexes.append(j)
            elif curr_city == opposite_city:
                opposite_indexes.append(j)
        else:
            other_indexes.append(j)

    return indexes, opposite_indexes, other_indexes


def calc_labels_positions(target_tags_table, opposite_tags_table,
                          indexes, visual_data,
                          min_dx=20.0, min_dy=10.0):

    def calc_dist(point, other_points):
        if other_points:
            x, y = point[0], point[1]
            return ((x - other_points[0]) ** 2 + (y - other_points[1]) ** 2) ** 0.5
        else:
            return np.array()

    tags = consts.SELECTED_TAGS
    np.random.shuffle(tags)

    idx2tag = {}
    for index, row in target_tags_table.iterrows():
        idx2tag[index] = location_tags(row)[0]

    for index, row in opposite_tags_table.iterrows():
        idx2tag[index + target_tags_table.shape[0]] = location_tags(row)[0]

    tags_positions = {}
    for tag in tags:
        xm, ym = [], []
        for j in indexes:
            if j in idx2tag.keys() and idx2tag[j] == tag:
                xc, yc = visual_data[0, j], visual_data[1, j]
                xm.append(xc)
                ym.append(yc)

        if xm and ym:
            tags_positions[tag] = [np.median(xm), np.median(ym)]

    scenes_labels, labels_coordinates = [], []
    for k in tags_positions:
        if not np.isnan(tags_positions[k][0]):
            scenes_labels.append(k)
            labels_coordinates.append(tags_positions[k])

    idx_show = []
    x_show, y_show = [], []
    for j, (x, y) in enumerate(labels_coordinates):
        dists = calc_dist([x, y], [x_show, y_show])
        if j:
            closest_point_idx = np.argmin(dists)
            dx = np.abs(x - x_show[closest_point_idx])
            dy = np.abs(y - y_show[closest_point_idx])
        else:
            dx, dy = MAX_INT, MAX_INT

        if dx > min_dx or dy > min_dy:
            idx_show.append(j)
            x_show.append(x)
            y_show.append(y)

    scenes_labels = [x for j, x in enumerate(scenes_labels)
                     if j in idx_show]

    labels_coordinates = [x for j, x in enumerate(labels_coordinates)
                          if j in idx_show]

    return scenes_labels, labels_coordinates


def draw_locations_scatter(locs_x, locs_y,
                           opposite_locs_x, opposite_locs_y,
                           locs_labels, opposite_locs_labels,
                           tag_labels, tag_labels_coordinates,
                           city, opposite_city):

    def create_scatter(x, y, colors, labels, name, size, opacity):
        return go.Scatter(x=x, y=y,
                          mode='markers',
                          hoverinfo='text+x+y',
                          text=labels, name=name,
                          marker=dict(size=size,
                                      color=colors,
                                      opacity=opacity))

    style = styles.LocationsScatterStyle

    annotations = []

    for l, x, y in zip(tag_labels,
                       [x[0] for x in tag_labels_coordinates],
                       [x[1] for x in tag_labels_coordinates]):
        annotations.append(go.layout.Annotation(x=x, y=y,
                                                xanchor="center",
                                                showarrow=False,
                                                text="<i><b>{}".format(l),
                                                opacity=style.ANNOTATION_OPACITY,
                                                bgcolor=style.ANNOTATION_BACKGROUND,
                                                font=dict(size=style.ANNOTATION_FONT_SIZE,
                                                          color=style.ANNOTATION_FONT_COLOR,
                                                          family=style.ANNOTATION_FONT_NAME)))

    data = [create_scatter(locs_x, locs_y,
                           style.TARGET_COLOR,
                           locs_labels, city,
                           style.MARKER_SIZE,
                           style.MARKER_OPACITY),

            create_scatter(opposite_locs_x, opposite_locs_y,
                           style.OPPOSITE_COLOR,
                           opposite_locs_labels,
                           opposite_city,
                           style.MARKER_SIZE,
                           style.MARKER_OPACITY)]

    axis_style = dict(showticklabels=False, zeroline=False)

    layout = go.Layout(height=style.PLOT_HEIGHT,
                       width=style.PLOT_WIDTH,
                       margin=style.MARGIN,
                       hovermode='closest',
                       xaxis=axis_style,
                       yaxis=axis_style)

    fig = go.Figure(data=data, layout=layout)
    fig['layout']['annotations'] = annotations
    py.iplot(fig, show_link=False)
