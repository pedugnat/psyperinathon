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
from utils import make_card_repartition, generate_hidden_divs, make_row
from model import process_values


# DASH AND APP SETTINGS
external_stylesheets = [dbc.themes.BOOTSTRAP]
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
            make_group("Variables économiques", items_economique),
            label="Variables économiques",
            tab_style=eq_width,
        ),
        dbc.Tab(
            make_group("Variables médicales", items_medical),
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

random_cost = np.random.randint(5, 10) + np.random.random()
charts_coll = dbc.Collapse(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(
                            f"Les coûts associés aux problèmes de santé mentale périnatale chaque année représentent: ",
                            style={"text-align": "center"},
                        ),
                        html.H2(id="total-couts", style={"text-align": "center"}),
                    ]
                ),
                html.Div(" ", style={"width": "10%"}),
                dbc.Col([html.Div(id="draw1")]),
            ],
        ),
    ],
    id="collapsed-graphs",
)


logo_alliance = "http://alliancefrancophonepourlasantementaleperinatale.com/wp-content/uploads/2020/03/cropped-cropped-cropped-alliance-francaise-AFSMP-2-1-300x246.png"
alliance = "Alliance francophone pour la santé mentale périnatale"

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=logo_alliance, height="60px")),
                    dbc.Col(dbc.NavbarBrand("Outil AFSMP")),
                ],
                align="center",
                no_gutters=False,
            ),
            href="http://alliance-psyperinat.org/",
            target="_blank",
            style={"float": "left"},
        ),
        html.Div(alliance, style={"float": "right"})
    ],
    color="light",
    light=True,
    sticky="top",
    className="container",
)


app.layout = dbc.Container(
    [
    	navbar,
        html.H1("Estimer le coût des maladies psypérinatales en France"),
        html.Hr(),
        tabs,
        html.Hr(),
        button_generate,
        html.Hr(),
        charts_coll,
        html.Hr(),
        html.H3("Tableaux récapitulatifs"),
        dbc.Row([dbc.Col([html.Div(id="table1")]),
        	dbc.Col([html.Div(id="table2")])
        	])
        ,
        #html.Div(id="table2"),
        #html.Div(id="draw1"),
    ]
    + generate_popovers()
    + generate_hidden_divs(),
)

"""global slider_values
slider_values = list()

def update_output(n_clicks, inp):
    time.sleep(0.01)
    slider_values.append(inp)
    return "Input is {}".format(inp)


for i in range(nb_variables_total):
    app.callback(
        Output(f"hidden-div-{i}", "children"),
        [Input("button-generate", "n_clicks")],
        [State(f"slider-{i}", "value")],
    )(update_output)"""


@app.callback(
    [
        Output("table1", "children"),
        Output("table2", "children"),
        Output("draw1", "children"),
        Output("total-couts", "children"),
    ],
    [Input("button-generate", "n_clicks")],
    [State(f'slider-{i}', "value") for i in range(nb_variables_total)],
)
def compute_costs(n, inp0, inp1, inp2, inp3, inp4, inp5, inp6, inp7, inp8, inp9, inp10, 
    inp11, inp12, inp13, inp14, inp15, inp16, inp17, inp18, inp19, inp20, inp21, inp22, 
    inp23, inp24, inp25, inp26, inp27, inp28, inp29, inp30, inp31, inp32, inp33, inp34, 
    inp35, inp36, inp37, inp38, inp39, inp40, inp41, inp42, inp43, inp44, inp45, inp46, 
    inp47, inp48, inp49, inp50, inp51, inp52, inp53, inp54, inp55, inp56, inp57, inp58, 
    inp59, inp60, inp61, inp62, inp63):

    sliders = eval(str([f'inp{i}' for i in range(df_variables.shape[0])]).replace("'", ''))

    df_variables["upd_variables"] = sliders

    df_par_cas = process_values(df_variables).reset_index()
    print(df_par_cas)


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

    df_par_naissance = df_par_cas.copy()
    df_par_naissance.iloc[:, 1:] = df_par_naissance.iloc[:, 1:].mul(prevalences, axis=0)


    cout_total = df_par_naissance['Total'].sum() * 753000
    cout_total_str = f"\n\n{cout_total / int(1e9): .1f} milliards d'euros par an", 


    card_repartition = make_card_repartition(df_par_naissance)


    def formating(x):
        return "{:,} €".format(x).replace(",", " ")

    for df in [df_par_cas, df_par_naissance]:    # formatte les 2 tableaux en euros 
	    for c in df.columns:
	        if df[c].dtype != "object":
	            df[c] = df[c].astype(int).apply(formating)

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

    return table_cas, table_naissance, card_repartition, cout_total_str


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
