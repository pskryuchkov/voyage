from collections import Counter
import operator
import matplotlib
import numpy as np

import pandas as pd

import plotly.graph_objs as go
import plotly.offline as py

from . import consts, shared, styles


def load_geo_table(city):
    geo_table = pd.read_csv(consts.ADRESSES_PATH.format(city),
                            error_bad_lines=False)

    geo_table = geo_table.drop_duplicates()

    geo_table[consts.STREET_COLUMN] = list(map(shared.title,
                                               geo_table[consts.STREET_COLUMN].tolist()))

    geo_table['longtitude'] = geo_table['longtitude'].astype(float)
    geo_table['latitude'] = geo_table['latitude'].astype(float)

    return geo_table


def count_activity(geo_table, shrink=True):
    streets = geo_table[consts.STREET_COLUMN].tolist()
    areas = geo_table[consts.osm_area_key].tolist()

    street_locations_n = sorted(Counter(streets).items(),
                                key=operator.itemgetter(1),
                                reverse=True)

    area_locations_n = sorted(Counter(areas).items(),
                              key=operator.itemgetter(1),
                              reverse=True)

    areas = [x[0] for x in area_locations_n]
    area_activity = [x[1] for x in area_locations_n]

    streets = [x[0] for x in street_locations_n]
    street_activity = [x[1] for x in street_locations_n]

    # FIXME: why 1?
    if shrink:
        areas = areas[1:consts.TOP_AREAS_N + 1]
        area_activity = area_activity[1:consts.TOP_AREAS_N + 1]

        streets = streets[1:consts.TOP_STREETS_N + 1]
        street_activity = street_activity[1:consts.TOP_STREETS_N + 1]

    return streets, street_activity, areas, area_activity


def count_streets_location(geo_table):
    avg_coords_table = geo_table[[consts.STREET_COLUMN,
                                  'longtitude',
                                  'latitude']].groupby(consts.STREET_COLUMN).agg(np.mean).reset_index()

    locations_counter_table = geo_table[consts.STREET_COLUMN].value_counts().reset_index()
    locations_counter_table.columns = [consts.STREET_COLUMN, 'counter']

    streets_table = pd.merge(avg_coords_table,
                             locations_counter_table,
                             on=consts.STREET_COLUMN).sort_values(by='counter', ascending=False)

    streets_table = streets_table[streets_table[consts.STREET_COLUMN] != 'None']

    return streets_table


def draw_city_map(lat, lon, streets, streets_locations_number, city_center):
    style = styles.CityMapStyle

    marker_sizes = [x if x < style.MAX_MARKER_SIZE else style.MAX_MARKER_SIZE 
                    for x in streets_locations_number]
    marker_sizes = [x if x > style.MIN_MARKER_SIZE else style.MIN_MARKER_SIZE
                    for x in marker_sizes]

    round3 = lambda x: round(float(x), 3)

    hover_template = "<i>{}</i><br>coords: {:.3f} {:.3f}<br>n_locations: {}"
    hover_func = lambda x, y, z, zz: hover_template.format(x, round3(y), round3(z), zz)
    scatter_hover = list(map(hover_func, streets, lat, lon, streets_locations_number))

    marker_labels = [str(x) if x >= 20 else "" for x in marker_sizes]

    data = [go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='markers',
                marker=dict(
                    size=marker_sizes,
                    color=style.MARKER_COLOR,
                    opacity=style.MARKER_OPACITY),
                text=scatter_hover,
                hoverinfo='text'),
            
           go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='text',
                marker=dict(
                    size=marker_sizes,
                    color=style.MARKER_COLOR,
                    opacity=style.MARKER_OPACITY),
                text=marker_labels,
                textfont=dict(color='darkred', family='arial'),
                hoverinfo='none')]

    layout = go.Layout(
                width=style.MAP_WIDTH,
                height=style.MAP_HEIGHT,
                hovermode='closest',
                margin=style.MARGIN, 
                showlegend=False,
                mapbox=dict(
                    accesstoken=consts.MAPBOX_TOKEN,
                    center=dict(
                        lat=city_center[0],
                        lon=city_center[1]),
                    zoom=style.ZOOM,
                    style='light'))

    fig = dict(data=data, layout=layout)
    py.iplot(fig, show_link=False)


def draw_street_area_combine(streets_barchart_y,
                             streets_barchart_x,
                             lat, lon,
                             areas_barchart_values,
                             areas_piechart_labels, language):
    style = styles.StreetAreaCombine

    colormap = matplotlib.cm.get_cmap(style.BAR_CHART_CM)

    norm_val = np.linspace(style.MAX_COLOR_VALUE,
                           style.MIN_COLOR_VALUE,
                           len(areas_barchart_values))

    pieces_colors = list(map(lambda x:
                             matplotlib.colors.rgb2hex(colormap(x)),
                             norm_val))

    round3 = lambda x: round(float(x), 3)
    hover_format = lambda x, y, z: "{}<br>{:.3f} {:.3f}".format(x, round3(y), round3(z))
    bar_hover = list(map(hover_format, streets_barchart_y, lat, lon))

    if language == 'ru':
        streets_barchart_y = list(map(shared.street_normalize_ru, streets_barchart_y))
        areas_piechart_labels = list(map(shared.area_normalize_ru, areas_piechart_labels))

    data = [go.Bar(y=streets_barchart_y,
                   x=streets_barchart_x,
                   marker=dict(color=style.BAR_CHART_COLOR),
                   orientation='h',
                   text=bar_hover,
                   hoverinfo='text',
                   opacity=style.BAR_CHART_OPACITY,
                   showlegend=False),

            go.Pie(values=areas_barchart_values,
                   labels=areas_piechart_labels,
                   domain=dict(x=style.PIE_AREA_X,
                               y=style.PIE_AREA_Y),
                   hoverinfo="label+percent+value",
                   textinfo='label+value',
                   textposition='outside',
                   hole=style.HOLE,
                   sort=False,
                   textfont=dict(size=style.PIE_CHART_FONT_SIZE,
                                 color=style.PIE_CHART_FONT_COLOR),
                   marker=dict(colors=pieces_colors),
                   pull=style.PULL)]

    layout = go.Layout(height=style.PLOT_HEIGHT,
                       width=style.PLOT_WIDTH,
                       showlegend=False,
                       margin=style.MARGIN,
                       hovermode='closest',
                       xaxis=dict(domain=style.BAR_CHART_AREA_X,
                                  tickfont=dict(color=style.BAR_CHART_FONT_COLOR,
                                                size=style.BAR_CHART_FONT_SIZE)),
                       yaxis=dict(domain=style.BAR_CHART_AREA_Y,
                                  autorange="reversed",
                                  ticklen=style.TICK_LEN,
                                  tickfont=dict(size=style.BAR_CHART_FONT_SIZE,
                                                color=style.BAR_CHART_FONT_COLOR)))
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, show_link=False)
