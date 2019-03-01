import numpy as np

import plotly.graph_objs as go
import plotly.offline as py

from . import consts, shared, styles


def process_face_data(loc_file, faces_json, streets_table, geo_table):
    id2loc = {x[0]: x[1] for x in loc_file}

    street_locations = []
    zero_counters, total_counters = [], []
    for location_id in geo_table['id']:
        if location_id in faces_json:
            zero_counters.append(faces_json[location_id].count('0'))
            total_counters.append(len(faces_json[location_id]))
        else:
            zero_counters.append(0)
            total_counters.append(0)

    geo_table1 = geo_table
    geo_table1['faces_zeros'] = zero_counters
    geo_table1['photos_total'] = total_counters

    data_dict = {}
    for x in streets_table[consts.STREET_COLUMN][:consts.N_STREETS]:
        data_submatrix = []
        for row in geo_table1.itertuples():
            if row.route == x:
                if row.photos_total > 0:
                    data_submatrix.append(1 - row.faces_zeros / row.photos_total)
                    street_locations.append(id2loc[str(row.id)])
        data_dict[x] = data_submatrix
    return data_dict, street_locations


def draw_face_scatter(input_data, street_locations, language):
    style = styles.FaceScatterStyle

    X, Y = [], []
    X_median, Y_median = [], []
    for j, y in enumerate(input_data):
        X += [y] * len(input_data[y])
        Y += input_data[y]
        X_median.append(y)
        Y_median.append(np.median(input_data[y]))

    if language == 'ru':
        X = list(map(shared.street_normalize_ru, X))
        X_median = list(map(shared.street_normalize_ru, X_median))

    trace = go.Scatter(x=Y, y=X,
                       mode='markers', name='locations',
                       text=street_locations, hoverinfo='text+x',
                       marker=dict(opacity=style.MARKER_OPACITY,
                                   size=style.MARKER_SIZE,
                                   color=style.MARKER_COLOR))

    trace1 = go.Scatter(x=Y_median, y=X_median,
                        mode='markers', name='medians',
                        marker=dict(size=style.MEDIAN_MARKER_SIZE,
                                    opacity=style.MEDIAN_MARKER_OPACITY,
                                    color=style.MEDIAN_MARKER_COLOR,
                                    line=dict(width=style.MEDIAN_LINEWIDTH, color=style.MEDIAN_MARKER_COLOR),
                                    symbol=style.MEDIAN_MARKER_SYMBOL))

    layout = go.Layout(height=style.PLOT_HEIGHT, width=style.PLOT_WIDTH,
                       showlegend=True, hovermode='closest',
                       xaxis=dict(range=[style.MIN_X, style.MAX_X],
                                  zeroline=False,
                                  tickfont=dict(size=style.FONT_SIZE,
                                                color=style.FONT_COLOR)),
                       yaxis=dict(zeroline=False, autorange='reversed',
                                  tickfont=dict(size=style.FONT_SIZE,
                                                color=style.FONT_COLOR),
                                  tickangle=0),
                       margin=style.MARGIN)

    fig = go.Figure(data=[trace, trace1], layout=layout)
    py.iplot(fig, show_link=False)
