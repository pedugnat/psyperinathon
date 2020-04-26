import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from itertools import chain
import base64


# CSS SETTINGS
eq_width = {"width": "20%", "text-align": "center"}
tt = {"always_visible": False, "placement": "topLeft"}

# VARIABLES
global df_variables
df_variables = pd.read_csv("bdd_variables.csv")


def generate_random_df():
    df = pd.DataFrame(data={"Maladie": ["Dépression", "Anxiété", "Psychose"]})
    df["Coût total"] = np.random.randint(0, 10) / np.arange(1, 4)
    df["Part Mères"] = np.random.random(size=3) / 2
    df["Part Bébés"] = 1 - df["Part Mères"]
    df["Part Santé Social"] = np.random.random(size=3) / 5
    df["Part Autre Secteur Public"] = np.random.random(size=3) / 5
    df["Part Société entière"] = (
        1 - df["Part Santé Social"] - df["Part Autre Secteur Public"]
    )

    df.set_index("Maladie")

    a = pd.DataFrame(["Total"] + list(df.sum(axis=0).values[1:] / 3)).T
    a.columns = df.columns
    df_final = pd.concat([df, a])
    df_final = df_final.set_index("Maladie")
    df_final = df_final.astype(float).round(3)

    return df_final


def make_group(title, items):
    """items est un dict sous forme : key = nom var ; value = widget"""
    # rd_cost_maladie = np.random.randint(0, 100000)

    dict_cost = {
        "Depression Mère": 24290,
        "Depression Bébé": 65641,
        "Anxiété Mère": 22073,
        "Anxiété Bébé": 14824,
        "Psychose Mère": 55335,
        "Psychose Bébé": 8893,
    }

    if title in ["Variables économiques", "Variables médicales"]:
        badge = html.Div("")

    else:
        badge = dbc.Badge(
            "{:,} € par cas".format(dict_cost[title]).replace(",", " "),
            color="secondary",
            className="ml-1",
            style={"float": "right"},
        )

    card_header = dbc.CardHeader(
        [dbc.Row([dbc.Col([html.B(title)]), dbc.Col([badge]),], align="start",)]
    )

    return dbc.Card(
        [card_header]
        + list(
            chain(
                *[
                    [
                        dbc.Row([html.Li(it), generate_qm(it)], justify="start"),
                        items[it][0],
                    ]
                    for it in items
                ]
            )
        ),
        color="dark",
        outline=True,
    )


def generate_qm(item):
    id_hash = df_variables[df_variables["nom_variable"] == item].index.values[0]
    question_mark = dbc.Badge("?", pill=True, color="light", id="badge_" + str(id_hash))

    return dbc.Col(question_mark, width=1)


def generate_popovers():
    popovers = list()
    for i in range(df_variables.shape[0]):
        pp = dbc.Popover(
            [
                dbc.PopoverHeader(df_variables.iloc[i, :]["nom_variable"]),
                dbc.PopoverBody(df_variables.iloc[i, :]["explication"]),
            ],
            id=f"popover-{i}",
            target=f"badge_{i}",
            is_open=False,
        )
        popovers.append(pp)
    return popovers


def make_row(it):
    return dbc.Row([dbc.Col(html.Label(it)), dbc.Col(question_mark)])


def make_card_repartition(df_par_naissance):

    total_mere = df_par_naissance["Mère"].sum()
    total_bebe = df_par_naissance["Bébé"].sum()

    proportion_mere = 100 * total_mere / (total_mere + total_bebe)

    image_filename = "card_image.png"
    encoded_image = base64.b64encode(open(image_filename, "rb").read())

    card = dbc.Row(
        [
            dbc.Col(
                [
                    html.Img(
                        src="data:image/png;base64,{}".format(encoded_image.decode()),
                        alt="Image non disponible",
                        width=130,
                    ),
                ],
                width=3,
            ),
            dbc.Col(
                [
                    html.H1(
                        f"{proportion_mere: .0f} %",
                        style={"color": "#1b75bc", "font-weight": "bold",},
                    ),
                    html.P("de ces coûts sont liés à la mère"),
                    html.H1(
                        f"{100 - proportion_mere: .0f} %",
                        style={"color": "#00cc66", "font-weight": "bold",},
                    ),
                    html.P("de ces coûts sont liés au bébé"),
                ],
                width=4,
            ),
        ],
        justify="center",
        align="center",
        no_gutters=False,
    )

    return card
