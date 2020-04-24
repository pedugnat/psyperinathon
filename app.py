# DASH IMPORTS
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table as dt

# OTHER IMPORTS
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from itertools import chain
import pandas as pd
import time

# LOCAL IMPORTS
from utils import generate_random_df, make_group, generate_popovers, generate_qm
from utils import make_card_repartition
from model import process_values


# DASH AND APP SETTINGS
external_stylesheets = [dbc.themes.DARKLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# CSS SETTINGS
eq_width = {"width": "20%", "text-align": "center", "font-weight": "bold"}
tt = {"always_visible": False, "placement": "topLeft"}

# VARIABLES
global df_variables
col_types = {"maxi": float, "mini": int, "val": float, "step": float}
df_variables = pd.read_csv("variables_bauer - Feuille 1.csv", dtype=col_types)
nb_variables_total = df_variables.shape[0]


def make_row(it):
    return (dbc.Row([dbc.Col(html.Label(it)), 
                     dbc.Col(question_mark)]))


def marker(num):
    return int(num) if num % 1 == 0 else num


def generate_item(df_variables, category):
    """df_variables : df avec les infos sur les variables
    category : str"""

    df_categ = df_variables[df_variables["category"] == category]

    dict_items = {
        row["nom_variable"]: [
            dcc.Slider(
                min=row.mini,
                max=row.maxi,
                value=row.val,
                step=row.step,
                tooltip=tt,
                marks={
                    marker(row.mini): {
                        "label": "{} {}".format(round(row.mini, 2), row.unit)
                    },
                    marker(row.val): {
                        "label": "{} {}".format(round(row.val, 2), row.unit)
                    },
                    marker(row.maxi): {
                        "label": "{} {}".format(round(row.maxi, 2), row.unit)
                    },
                },
                id=f"slider-{idx}",
            )
        ]
        for idx, row in df_categ.iterrows()
    }

    return dict_items


def generate_hidden_divs():
    return [
        html.Div(id=f"hidden-div-{i}", hidden=True) for i in range(nb_variables_total)
    ]


# DEPRESSION
items_depression_mere = generate_item(df_variables, "depression_mere")
items_depression_bebe = generate_item(df_variables, "depression_bebe")


# ANXIETE
items_anxiete_mere = generate_item(df_variables, "anxiete_mere")
items_anxiete_bebe = generate_item(df_variables, "anxiete_bebe")


# PSYCHOSE
items_psychose_mere = generate_item(df_variables, "psychose_mere")
items_psychose_bebe = generate_item(df_variables, "psychose_bebe")


# MEDICAL ET ECONOMIQUE
items_economique = generate_item(df_variables, "economique")
items_medical = generate_item(df_variables, "medical")


tabs = dbc.Tabs(
    [
        dbc.Tab(
            make_group("Variables économiques", items_economique, is_maladie=False),
            label="Variables économiques",
            tab_style=eq_width,
        ),
        dbc.Tab(
            make_group("Variables médicales", items_medical, is_maladie=False),
            label="Variables médicales",
            tab_style=eq_width,
        ),
        dbc.Tab(
            [
                make_group("Depression Mère", items_depression_mere),
                html.Hr(),
                make_group("Depression Bébé", items_depression_bebe),
            ],
            label="Dépression",
            tab_style=eq_width,
        ),
        dbc.Tab(
            [
                make_group("Anxiété Mère", items_anxiete_mere),
                html.Hr(),
                make_group("Anxiété Bébé", items_anxiete_bebe),
            ],
            label="Anxiété",
            tab_style=eq_width,
        ),
        dbc.Tab(
            [
                make_group("Psychose Mère", items_psychose_mere),
                html.Hr(),
                make_group("Psychose Bébé", items_psychose_bebe),
            ],
            label="Psychose",
            tab_style=eq_width,
        ),
    ]
)


button_generate = dbc.Button(
    "Générer l'estimation !", color="primary", block=True, id="button-generate",
)

df_final = generate_random_df()


# PIE CHART
df_pie = df_final.iloc[:-1, :-1]
pie_maladies = px.pie(
    df_pie,
    values="Coût total",
    names=df_pie.index,
    title="Répartition des coûts par maladie (en %)",
    width=800,
    height=400,
)

pie_maladies.update_traces(textposition="inside", textinfo="percent+label")

random_cost = np.random.randint(5, 10) + np.random.random()
charts_coll = dbc.Collapse(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(
                            f"Les coûts associés aux problèmes de santé mentale périnatale chaque année représentent: "
                        ),
                        html.H2(f"\n\n{random_cost: .2f} milliards d'€"),
                    ]
                ),
                dbc.Col([dcc.Graph(id="example-graph-pie", figure=pie_maladies)]),
            ]
        ),
    ],
    id="collapsed-graphs",
)

app.layout = dbc.Container(
    [
        html.H1("Estimer le coût des maladies psypérinatales en France"),
        tabs,
        html.Hr(),
        button_generate,
        html.Hr(),
        charts_coll,
        html.Hr(),
        html.H3("Tableaux récapitulatifs"),
        html.Div(id="table1"),
        html.Div(id="table2"),
        html.Div(id="draw1"),
    ]
    + generate_popovers()
    + generate_hidden_divs()
)

global slider_values
slider_values = list()


def update_output(n_clicks, inp):
    time.sleep(0.01)
    slider_values.append(inp)
    return "Input is {}".format(inp)


for i in range(nb_variables_total):
    if i % 10 == 0:
        print(slider_values)

    app.callback(
        Output(f"hidden-div-{i}", "children"),
        [Input("button-generate", "n_clicks")],
        [State(f"slider-{i}", "value")],
    )(update_output)


@app.callback(
    [
        Output("table1", "children"),
        Output("table2", "children"),
        Output("draw1", "children"),
    ],
    [Input("button-generate", "n_clicks")],
)
def compute_costs(n):
    time.sleep(0.6)
    try:
        print("\nupdated values\n")
        df_variables["upd_variables"] = slider_values[-nb_variables_total:]
    except ValueError:
        print("\n did not update\n")
        df_variables["upd_variables"] = df_variables["val"]

    print(
        df_variables.set_index("nom_variable")
        .loc[
            [
                "Prix d'une vie",
                "Valeur d'une année de QALY",
                "Indice de perte de qualité de vie",
                "Perte de qualité de vie pour une psychose",
                "Proba suppl. de naissance prématurée si dépression",
            ]
        ]
        .iloc[:, -1]
    )

    df_par_cas = process_values(df_variables).reset_index()

    prevalences = (
        df_variables.set_index("nom_variable")
        .loc[
            [
                "Prévalence de la dépression",
                "Prévalence de l'anxiété",
                "Prévalence de la psychose",
            ]
        ]
        .iloc[:, -1]
        .values
        / 100
    )
    # print(prevalences)
    df_par_naissance = df_par_cas.copy()
    df_par_naissance.iloc[:, 1:] = df_par_naissance.iloc[:, 1:].mul(prevalences, axis=0)

    card_repartition = make_card_repartition(df_par_naissance)

    def formating(x):
        return "{:,} €".format(x).replace(",", " ")

    for c in df_par_cas.columns:
        if df_par_cas[c].dtype != "object":
            df_par_cas[c] = df_par_cas[c].astype(int).apply(formating)

    for c in df_par_naissance.columns:
        if df_par_naissance[c].dtype != "object":
            df_par_naissance[c] = df_par_naissance[c].astype(int).apply(formating)

    df_par_cas.columns = [
        c if i > 0 else "Coût par cas" for i, c in enumerate(df_par_cas.columns)
    ]
    df_par_naissance.columns = [
        c if i > 0 else "Coût par naissance"
        for i, c in enumerate(df_par_naissance.columns)
    ]

    table_cas = dbc.Table.from_dataframe(
        df_par_cas, striped=True, bordered=True, hover=True
    )
    table_naissance = dbc.Table.from_dataframe(
        df_par_naissance, striped=True, bordered=True, hover=True
    )
    return table_cas, table_naissance, card_repartition


# CALLBACK GRAPHS
@app.callback(
    Output("collapsed-graphs", "is_open"),
    [Input("button-generate", "n_clicks")],
    [State("collapsed-graphs", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# CALLBACK POPOVERS
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open


for i in range(nb_variables_total):
    app.callback(
        Output(f"popover-{i}", "is_open"),
        [Input(f"badge_{i}", "n_clicks")],
        [State(f"popover-{i}", "is_open")],
    )(toggle_popover)


if __name__ == "__main__":
    app.run_server(
        debug=False, port=8890,
    )
