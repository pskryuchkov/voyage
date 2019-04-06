import numpy as np

import pandas as pd

import plotly.graph_objs as go
import plotly.offline as py

import voyage.consts as consts
import voyage.styles as styles


def trim(s, max_len=20):
    if len(s) <= max_len:
        return s
    else:
        s = s[:max_len].strip("_")
        return s + "..."


def tuple_to_str(t):
    return '{}, {}'.format(trim(t[0].replace("_", " ").strip()), t[1])


def remove_stopwords(df, column, stopwords):
    for word in stopwords:
        df = df[df[column].map(lambda x: not word in x.lower().split())]
    return df


def get_wiki_locations(wiki_df, min_locations=20):
    if wiki_df.dropna(subset=['roads']).shape[0] < min_locations:
        print("WARNING: too few wiki locations")
        return pd.DataFrame()

    wiki_df['street'] = wiki_df['roads']
    wiki_df = wiki_df.drop(columns=['roads'])
    wiki_df = wiki_df[wiki_df['street'] != '']

    wiki_df.views = wiki_df.views.astype(int)
    wiki_df.lon = wiki_df.lon.astype(float)
    wiki_df.lat = wiki_df.lat.astype(float)
    wiki_df['street'] = wiki_df['street'].astype(str)

    wiki_df['street'] = list(map(lambda x: x.title(),
                                 wiki_df['street']))

    stopwords = ['nazi']
    wiki_df = remove_stopwords(wiki_df, 'wiki_name', stopwords)

    return wiki_df


def get_street_wiki_views(wiki_df):
    street_wiki_df = wiki_df[['views', 'street']]

    street_wiki_df = street_wiki_df.groupby(['street']) \
        .sum() \
        .sort_values(by=['views'], ascending=False) \
        .reset_index()

    return {x: y for x, y in zip(street_wiki_df['street'],
                                 street_wiki_df['views'])}


def get_insta_dict(insta_df, geo_table):
    loc_id = []
    for x in insta_df.link:
        loc_id.append(x.split("/")[3])

    insta_df['id'] = loc_id

    # TEST ME
    insta_df = insta_df.drop([0])

    insta_df.id = insta_df.id.astype(int)
    geo_table.id = geo_table.id.astype(int)
    photos_top_streets = pd.merge(insta_df, geo_table, on='id') \
        [[consts.STREET_KEY, 'photos_counter']]

    photos_top_streets = photos_top_streets.groupby([consts.STREET_KEY]) \
        .sum() \
        .sort_values(by=['photos_counter'], ascending=False) \
        .reset_index()

    photos_top_streets = photos_top_streets[photos_top_streets[consts.STREET_KEY] != 'None']
    photos_top_streets['photos_counter'] = \
        photos_top_streets['photos_counter'].astype(int)

    return {x: y for x, y in zip(photos_top_streets[consts.STREET_KEY].tolist(),
                                 photos_top_streets['photos_counter'] \
                                 .tolist())}


def get_street_locs(wiki_locations_df):
    max_locs = 5

    grouped = wiki_locations_df[['street', 'wiki_name', 'views']].groupby('street')

    street_locs_wiki = {}
    for street, group in grouped:
        locs = list(zip(group.wiki_name.tolist(), group.views.tolist()))
        street_locs_wiki[street] = locs[:max_locs]

    return street_locs_wiki


def get_wiki_data(street_insta_dict, street_wiki_dict, street_locs_wiki):
    labels_wiki, short_labels = [], []
    xc, yc = [], []
    for z in street_insta_dict:
        if z in street_wiki_dict:
            short_labels.append(z)
            xc.append(street_insta_dict[z])
            yc.append(street_wiki_dict[z])

            sorted_labels = sorted(street_locs_wiki[z], key=lambda x: x[1], reverse=True)
            labels_wiki.append('<i>{}</i><br>{}'.format(z,
                                                        "<br>".join(map(tuple_to_str,
                                                                        sorted_labels))))
        else:
            continue

    wiki_data = {}
    for u, x, y, z in zip(short_labels, xc, yc, labels_wiki):
        wiki_data[u] = [x, y, z]

    return wiki_data


def draw_insta_wiki_scatter(scatter_x1, scatter_y1, scatter_labels1):
    style = styles.InstaWikiScatterStyle

    
    min_x, max_x = np.min(scatter_x1), np.max(scatter_x1)
    min_y, max_y = np.min(scatter_y1), np.max(scatter_y1)
    med_x = np.median(scatter_x1)
    med_y = np.median(scatter_y1)

    left_bound = min_x * (1 - style.AXIS_DELTA)
    right_bound = max_x * (1 + style.AXIS_DELTA)

    lower_bound = min_y * (1 - style.AXIS_DELTA)
    upper_bound = max_y * (1 + style.AXIS_DELTA)

    lines_style = dict(color=style.LINE_COLOR,
                       width=style.LINE_WIDTH,
                       dash=style.LINE_STYLE)

    data = [go.Scatter(x=scatter_x1, y=scatter_y1,
                       text=scatter_labels1,
                       mode='markers',
                       hoverinfo='text',
                       name='streets',
                       showlegend=True,
                       textfont=dict(size=style.FONT_SIZE,
                                     color=style.FONT_COLOR),
                       marker=dict(color=style.MARKER_COLOR,
                                   opacity=style.MARKER_OPACITY)),

            go.Scatter(x=[left_bound, right_bound],
                       y=[med_y, med_y],
                       name='median',
                       mode='lines',
                       hoverinfo='none',
                       showlegend=True,
                       line=lines_style),

            go.Scatter(x=[med_x, med_x],
                       y=[lower_bound, upper_bound],
                       mode='lines',
                       hoverinfo='none',
                       showlegend=False,
                       line=lines_style)]

    layout = go.Layout(width=style.PLOT_WIDTH,
                       height=style.PLOT_HEIGHT,
                       margin=style.MARGIN,
                       xaxis=dict(title='insta',
                                  type=style.AXIS_TYPE),
                       yaxis=dict(title='wiki',
                                  type=style.AXIS_TYPE),
                       hovermode='closest')

    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, show_link=False)




