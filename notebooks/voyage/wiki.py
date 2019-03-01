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


def get_wiki_locations(wiki_df):
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
        [[consts.STREET_COLUMN, 'photos_counter']]

    photos_top_streets = photos_top_streets.groupby([consts.STREET_COLUMN]) \
        .sum() \
        .sort_values(by=['photos_counter'], ascending=False) \
        .reset_index()

    photos_top_streets = photos_top_streets[photos_top_streets[consts.STREET_COLUMN] != 'None']
    photos_top_streets['photos_counter'] = \
        photos_top_streets['photos_counter'].astype(int)

    return {x: y for x, y in zip(photos_top_streets[consts.STREET_COLUMN].tolist(),
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
            labels_wiki.append('<i>{}</i><br>{}'.format(z,
                                                        "<br>".join(map(tuple_to_str,
                                                                        street_locs_wiki[z]))))
        else:
            continue

    wiki_data = {}
    for u, x, y, z in zip(short_labels, xc, yc, labels_wiki):
        wiki_data[u] = [x, y, z]

    return wiki_data


def draw_insta_wiki_scatter(scatter_x1, scatter_y1, scatter_labels1):
    style = styles.InstaWikiScatterStyle

    data = [go.Scatter(x=scatter_x1, y=scatter_y1,
                       text=scatter_labels1,
                       mode='markers',
                       hoverinfo='text',
                       name='huge',
                       textfont=dict(size=8, color='lightgrey'),
                       marker=dict(color='dodgerblue', opacity=0.8)),
            ]

    med_x = np.median(scatter_x1)
    med_y = np.median(scatter_y1)

    shapes = [dict(type='line',
                   xref='x', yref='paper',
                   x0=med_x, y0=0,
                   x1=med_x, y1=1,
                   line=dict(color='grey', width=2, dash='dash')),
              dict(type='line',
                   xref='paper', yref='y',
                   x0=0, y0=med_y,
                   x1=1, y1=med_y,
                   line=dict(color='grey', width=2, dash='dash'))]

    layout = go.Layout(width=style.PLOT_WIDTH,
                       height=style.PLOT_HEIGHT,
                       margin=go.layout.Margin(t=30, b=50, l=50, r=30),
                       xaxis=dict(
                           title='insta', type='log',
                       ),
                       yaxis=dict(
                           title='wiki', type='log'),
                       hovermode='closest',
                       shapes=shapes,
                       showlegend=False)

    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, show_link=False)




