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


# CSS SETTINGS
eq_width = {"width": "20%", "text-align": "center"}
tt = {"always_visible": False, "placement": "topLeft"}

# VARIABLES
global df_variables
df_variables = pd.read_csv("variables_bauer - Feuille 1.csv")


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
    rd_cost_maladie = np.random.randint(0, 100000)

    card_header = dbc.CardHeader(
        [
            dbc.Row(
                [
                    dbc.Col([html.B(title)]),
                    dbc.Col(
                        [
                            dbc.Badge(
                                "{:,} € par cas".format(rd_cost_maladie).replace(
                                    ",", " "
                                ),
                                color="secondary",
                                className="ml-1",
                            )
                        ]
                    ),
                ],
                align="start",
            )
        ]
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
