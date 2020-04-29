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
from utils import make_group, generate_popovers, generate_qm
from utils import make_card_repartition, make_row, millify, generate_form_naissances
from model import process_values
from table_mod import generate_table_from_df


# DASH AND APP SETTINGS
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# CSS SETTINGS
eq_width = {"width": "25%", "text-align": "center", "font-weight": "bold"}
tt = {"always_visible": False, "placement": "topLeft"}

# VARIABLES
global df_variables
col_types = {"maxi": float, "mini": int, "val": float, "step": float}
df_variables = pd.read_csv("bdd_variables.csv", dtype=col_types)
nb_variables_total = df_variables.shape[0]


def marker(num):
    return int(num) if num % 1 == 0 else num


def generate_item(df_variables, category):
    """df_variables : df avec les infos sur les variables
    category : str"""

    df_categ = df_variables[df_variables["category"] == category]

    dict_items = {
        row["nom_variable"]: [
            html.Div(
                [
                    dcc.Slider(
                        min=row.mini,
                        max=row.maxi,
                        value=row.val,
                        step=row.step,
                        tooltip=tt,
                        marks={
                            marker(row.mini): {
                                "label": "{}\xa0{}".format(round(row.mini, 2), row.unit)
                            },
                            marker(row.val): {
                                "label": "{}\xa0{}".format(round(row.val, 2), row.unit)
                            },
                            marker(row.maxi): {
                                "label": "{}\xa0{}".format(round(row.maxi, 2), row.unit)
                            },
                        },
                        id=f"slider-{idx}",
                    ),
                ],
                style={"padding": "0 1em 0 1em"},
                hidden=bool(row["nom_variable"] == "Nombre de naissances"),
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


tabs_variables = dbc.Tabs(
    [
        dbc.Tab(
            make_group("Variables médicales", items_medical),
            label="Variables médicales",
            tab_style=eq_width,
        ),
        dbc.Tab(
            make_group("Variables économiques", items_economique),
            label="Variables économiques",
            tab_style=eq_width,
        ),
    ],
)

tabs_maladies = dbc.Tabs(
    [
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
    ],
)


button_generate = dbc.Button(
    "Générer l'estimation !",
    color="primary",
    block=True,
    id="button-generate",
    size="lg",
)


charts_coll = dbc.Collapse(
    [
        html.H3("Principaux enseignements", style={"color": "#8ec63f"}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(
                            f"Avec ces paramètres, les coûts associés aux problèmes de santé mentale périnatale représentent chaque année :",
                            style={"text-align": "center"},
                        ),
                        html.H1(id="total-couts", style={"text-align": "center"}),
                    ],
                    style={"border": "0px solid black", "padding": "10% 2% 0 0"},
                ),
                # html.Div(" ", style={"width": "5%"}),
                dbc.Col(
                    [html.Div(id="draw1")],
                    style={"border": "0px solid black", "padding": "5% 0 0 2%"},
                ),
                dbc.Col(
                    [dcc.Graph(id="example-graph-pie")],
                    style={"border": "0px solid black", "padding": "5% 0 0 0"},
                ),
            ],
        ),
        html.H3("Tableaux récapitulatifs", style={"color": "#8ec63f"}),
        dbc.Row([dbc.Col([html.Div(id="table1")]), dbc.Col([html.Div(id="table2")])]),
        html.Hr(),
    ],
    id="collapsed-graphs",
)


logo_alliance = "http://alliancefrancophonepourlasantementaleperinatale.com/wp-content/uploads/2020/03/cropped-cropped-cropped-alliance-francaise-AFSMP-2-1-300x246.png"

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=logo_alliance, height="70px")),
                    dbc.Col(dbc.NavbarBrand("Outil Psython")),
                ],
                align="center",
                no_gutters=False,
            ),
            href="http://alliance-psyperinat.org/",
            target="_blank",
            style={"float": "left"},
        ),
        html.P(
            "Alliance francophone pour la santé mentale périnatale",
            style={"margin-left": "auto", "margin-right": "0"},
        ),
    ],
    color="#1b75bc",
    light=True,
    sticky="top",
    className="container",
)

pitch_text = "Les Anglais ont compris dès 2014 l’importance d’investir sur les générations futures en finançant massivement la santé mentale périnatale. C’est notamment sous l’impulsion de l’article The costs of perinatal mental health problems, écrit par des chercheurs de la London School of Economics, que le gouvernement Cameron a investit 300 millions de livres pour amorcer sa politique, et maintient désormais un financement annuel de 100 millions de livres (source ?). Pour mieux comprendre la nécessité de prendre en compte cet aspect de nos politiques de santé, et notamment dans une perspective d’investissement social, l’Alliance Francophone pour la Santé Mentale Périnatale a créé un simulateur qui réplique le modèle médico-économique de l’article Bauer et al. afin d’estimer le coût des maladies psychiatriques périnatales en France."

pitch = html.Div(
    [
        html.H3("Introduction à l'outil", style={"color": "#8ec63f"}),
        html.Div([html.Span(pitch_text)], style={'text-align': "justify"}),
    ],
    style={"border": "0px solid black", "padding": "1em 1em 1em 1em"},
)

mode_demploi_text = {
    "mode_demploi_1": "Premièrement, il vous faudra choisir l’échelle à laquelle vous voulez évaluer le coût des maladies périnatales. Il est possible de choisir la France, l’une des 12 régions, l’un des 100 départements, l’une des 200 plus grandes villes ou l'une des 577 circonscriptions. Lorsque vous sélectionnez un territoire, le nombre de naissances en 2018 sur le territoire apparaît à droite. Vous pouvez toujours modifier directement ce chiffre à la main.",
    "mode_demploi_2": "Deuxièmement, il vous faudra ajuster les principales variables qui influent sur le modèle. En effet, notre modélisation est fondée sur des hypothèses (les plus crédibles selon nous), mais il vous est possible de les ajuster pour refléter au mieux vos convictions et vos hypothèses. Par exemple, il est difficile de connaître précisément la prévalence de la dépression périnatale en France, mais les estimations communément admises sont de 10%. Libre à vous de modifier la valeur si vous pensez que cette estimation est incorrecte.",
    "mode_demploi_3": "Troisièmement, si vous souhaitez aller plus loin dans l’utilisation de l’outil, il est possible de modifier toutes les hypothèses initiales de l'article, mais celles-ci sont plus techniques. Par exemple, vous aurez la possibilité de modifier le coût d’une hospitalisation liée à une dépression, ou encore les coûts supplémentaires pour la justice des problèmes de conduite liés à l’anxiété périnatale.",
    "mode_demploi_4": "Une fois ces trois étapes remplies, il vous suffira de cliquer sur 'Générer l’estimation' et une interface récapitulative des coûts à votre échelle et avec vos hypothèses apparaîtra : c’est le coût lié aux maladies psychiques périnatales ! Tout au long de votre parcours, n’hésitez pas à appuyer sur les petits points d’interrogation, ils vous donneront des informations supplémentaires.",
}

mode_demploi = html.Div(
    [
        html.H3("Mode d'emploi", style={"color": "#8ec63f"}),
        html.Div(
            html.Ul(
                [
                    html.Li(html.Span(parag), style={"margin": "0 0 0.7em 0"})
                    for parag in mode_demploi_text.values()
                ],
                style={"list-style-position": "outside", 'text-align': "justify"},
            ),
        ),
    ],
    style={"border": "1px solid black", "padding": "1em 1em 1em 1em"},
)

global bdd_naissances
bdd_naissances = pd.read_csv("naissance_echelons.csv")

form_naissances = generate_form_naissances(bdd_naissances)

title = html.H1(
    "Estimer le coût des maladies psypérinatales",
    style={"padding": "1em 0 1em 0", "text-align": "center", "color": "#1b75bc"},
)

tabs_and_title_variables = html.Div(
    [
        html.H2(
            "Deuxième étape : ajustement des variables principales",
            style={"color": "#8ec63f"},
        ),
        tabs_variables,
    ],
    style={"padding": "0.5em 0 0.5em 0"},
)

tabs_and_title_maladies = html.Div(
    [
        html.H2(
            "Troisième étape : pour aller plus loin...", style={"color": "#8ec63f"}
        ),
        tabs_maladies,
    ],
    style={"padding": "0.5em 0 0.5em 0"},
)

app.layout = dbc.Container(
    [
        navbar,
        title,
        pitch,
        html.Hr(),
        mode_demploi,
        html.Hr(),
        form_naissances,
        html.Hr(),
        tabs_and_title_variables,
        html.Hr(),
        tabs_and_title_maladies,
        html.Hr(),
        button_generate,
        html.Hr(),
        charts_coll,
    ]
    + generate_popovers(),
    id="main-container"
)


@app.callback(Output("nombre-naissances", "value"), [Input("dd-echelle", "value")])
def upd_input_echelle(val):
    return val


@app.callback(
    [
        Output("table1", "children"),
        Output("table2", "children"),
        Output("draw1", "children"),
        Output("total-couts", "children"),
        Output("example-graph-pie", "figure"),
    ],
    [Input("button-generate", "n_clicks"), Input("nombre-naissances", "value")],
    [State(f"slider-{i}", "value") for i in range(nb_variables_total)],
)
def compute_costs(n, n_naissances, *sliders):
    df_variables_upd = df_variables.copy()
    df_variables_upd["upd_variables"] = sliders

    df_par_cas, df_repartition = process_values(df_variables_upd)
    df_par_cas = df_par_cas.reset_index()
    print(df_par_cas)

    prevalences = (
        df_variables_upd.set_index("nom_variable")
        .loc[
            [
                "Prévalence de " + mal
                for mal in ["la dépression", "l'anxiété", "la psychose"]
            ]
        ]
        .iloc[:, -1]
        .values
        / 100
    )

    df_par_naissance = df_par_cas.copy()
    df_par_naissance.iloc[:, 1:] = df_par_naissance.iloc[:, 1:].mul(prevalences, axis=0)

    for df in [df_par_cas, df_par_naissance]:
        df.loc["3 maladies"] = ["Total des trois maladies"] + np.sum(
            df.values[:, 1:], axis=0
        ).tolist()

    total_par_cas = df_par_naissance["Total"].iloc[:-1].sum()

    print(f"Nombre naissances = {n_naissances}")
    if n_naissances is None:
        n_naissances = 1  # set 1 as default to avoid problems if values is not defined

    cout_total = total_par_cas * n_naissances
    cout_total_str = millify(cout_total)
    print(cout_total_str)

    df_repartition["couts_totaux"] = (
        df_repartition["Répartition des coûts par secteur"] * cout_total
    )
    df_repartition["couts_lisibles"] = df_repartition["couts_totaux"].apply(millify)

    pie_maladies = px.pie(
        df_repartition,
        values="couts_totaux",
        names=df_repartition.index,
        title="<b>Répartition des coûts par secteur</b>",
        width=350,
        height=350,
        color="couts_totaux",
        color_discrete_sequence=["#d91b5c", "#f7a5ab", "#8ec63f"],
    )

    pie_maladies.update_traces(
        textposition="auto",
        textinfo="label+percent",
        insidetextorientation="horizontal",
        sort=False,
        customdata=df_repartition["couts_lisibles"],
        hovertemplate="<b>%{label}</b><br>Coût : %{customdata[0]}",
    )
    pie_maladies.update_layout(showlegend=False)

    card_repartition = make_card_repartition(df_par_naissance)

    def formating(x):
        return "{:,} €".format(x).replace(",", " ")

    for df in [df_par_cas, df_par_naissance]:  # formatte les 2 tableaux en euros
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

    table_cas = generate_table_from_df(
        dbc.Table,
        df_par_cas,
        striped=True,
        bordered=True,
        hover=True,
        italic_last=True,
    )

    table_naissance = generate_table_from_df(
        dbc.Table,
        df_par_naissance,
        striped=True,
        bordered=True,
        hover=True,
        italic_last=True,
    )

    return table_cas, table_naissance, card_repartition, cout_total_str, pie_maladies


# CALLBACK GRAPHS
@app.callback(
    Output("collapsed-graphs", "is_open"),
    [Input("button-generate", "n_clicks")],
    [State("collapsed-graphs", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return True
    return is_open


def toggle_collapse_maladies(n, is_open):
    if n:
        return not is_open
    return is_open


for item_maladie in [
    "Depression-Mère",
    "Depression-Bébé",
    "Anxiété-Mère",
    "Anxiété-Bébé",
    "Psychose-Mère",
    "Psychose-Bébé",
]:
    app.callback(
        Output(f"collapsible-{item_maladie}", "is_open"),
        [Input(f"open-tab-{item_maladie}", "n_clicks")],
        [State(f"collapsible-{item_maladie}", "is_open")],
    )(toggle_collapse_maladies)

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
