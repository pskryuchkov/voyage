import numpy as np

from sklearn.manifold import TSNE

import plotly.graph_objs as go
import plotly.offline as py

from . import consts, scenes, shared, styles


def to_planar(features_table):
    planar_features = TSNE().fit_transform(features_table).T
    return planar_features


def short_tag(x):
    return x.split("/")[0]


def location_tags(features, n_top=3):
    top_idx = np.argsort(features[consts.SELECTED_TAGS].tolist())[-n_top:][::-1]
    top_tags = [short_tag(consts.SELECTED_TAGS[x]) for x in top_idx]
    return top_tags


def get_cloud_hovers(locations_data, photos_scenes):
    id2loc_target = scenes.get_id2loc(locations_data)

    id2tags = {}
    for index, row in photos_scenes.iterrows():
        id2tags[row['id']] = location_tags(row)

    hovers = ["{}<br>{}".format(shared.trim(id2loc_target[x].replace("_", " ")),
                                       ", ".join(id2tags[x]))
                     if x in id2loc_target else "_"
                     for x in photos_scenes['id'].tolist()]
    return hovers


def separate_indexes(city, opposite_city,
                     points, ordered_ids, id2city,
                     n_neighbors=10, bro_threshold=0.7):

    def sort_by_dist(node, nodes):
        dist_2 = np.sum((np.asarray(nodes) - node) ** 2, axis=1)
        return np.argsort(dist_2)

    visual_data_list = list(points.T)

    n_points = len(points[0])
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


def calc_tags_positions(target_tags_table, opposite_tags_table,
                        indexes, visual_data,
                        min_hor_diff=8.0,
                        min_ver_diff=8.0):

    def min_diff(z, zarr):
        if len(zarr) > 1:
            return np.sort(np.abs(z - zarr))[1]
        else:
            return 10 ** 6

    idx2tag = {}
    for index, row in target_tags_table.iterrows():
        idx2tag[index] = location_tags(row)[0]

    for index, row in opposite_tags_table.iterrows():
        idx2tag[index + target_tags_table.shape[0]] = location_tags(row)[0]

    tags_positions = {}
    for tag in consts.SELECTED_TAGS:
        xm, ym = [], []
        for j in indexes:
            if j in idx2tag.keys() and idx2tag[j] == tag:
                xc, yc = visual_data[0, j], visual_data[1, j]
                xm.append(xc)
                ym.append(yc)

        if xm and ym:
            tags_positions[tag] = [np.mean(xm), np.mean(ym)]

    tag_labels, tag_labels_coordinates = [], []
    for k in tags_positions:
        if not np.isnan(tags_positions[k][0]):
            tag_labels.append(k)
            tag_labels_coordinates.append(tags_positions[k])

    showing_indexes = []
    xarr, yarr = [], []
    for j, (x, y) in enumerate(tag_labels_coordinates):
        dx, dy = min_diff(x, xarr), min_diff(y, yarr)
        if (dx > min_hor_diff and dy > min_ver_diff):
            showing_indexes.append(j)
            xarr.append(x)
            yarr.append(y)

    tag_labels = [x for j, x in enumerate(tag_labels)
                  if j in showing_indexes]

    tag_labels_coordinates = [x for j, x in enumerate(tag_labels_coordinates)
                              if j in showing_indexes]

    return tag_labels, tag_labels_coordinates


def draw_locations_scatter(locs_x, locs_y,
                           opposite_locs_x, opposite_locs_y,
                           locs_labels, opposite_locs_labels,
                           tag_labels, tag_labels_coordinates,
                           city, opposite_city):

    def create_scatter(x, y, colors, labels, name, size, opacity):
        return go.Scatter(x=x, y=y,
                          mode='markers',
                          hoverinfo='text',
                          text=labels, name=name,
                          marker=dict(size=size,
                                      color=colors,
                                      opacity=opacity))

    style = styles.LocationsScatterStyle

    annotations = []

    for l, x, y in zip(tag_labels,
                       [x[0] for x in tag_labels_coordinates],
                       [x[1] for x in tag_labels_coordinates]):
        annotations.append(
            go.layout.Annotation(x=x, y=y,
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
