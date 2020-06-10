import pandas as pd
import numpy as np
import base64
import math
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go

from itertools import chain
from dash.dependencies import Input, Output, State


# CSS SETTINGS
eq_width = {"width": "20%", "text-align": "center"}
tt = {"always_visible": False, "placement": "topLeft"}

# VARIABLES
global df_variables
df_variables = pd.read_csv("bdd_variables.csv")

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


def make_group(title, items, item_name):
    """items est un dict sous forme : key = nom var ; value = widget"""
    # rd_cost_maladie = np.random.randint(0, 100000)
    #item_name = "-".join(title.split()[:2])

    if title in ["Variables économiques", "Variables médicales"]:
        button_open_tab = html.Div("")

    else:
        button_open_tab = dbc.Button(
            "Ouvrir l'onglet",
            color="secondary",
            className="ml-1",
            size="sm",
            style={"float": "right"},
            id=f"open-tab-{item_name}",
        )

    card_header = dbc.CardHeader(
        [dbc.Row([dbc.Col([html.B(title)]), dbc.Col([button_open_tab])])]
    )

    card_content = list(
        chain(
            *[
                [
                    dbc.Row(
                        [
                            html.Li(it, style={"padding": "5px 5px 5px 40px"}),
                            generate_qm(it),
                        ],
                        justify="start",
                    ),
                    items[it][0],
                ]
                for it in items
            ]
        )
    )

    if title not in ["Variables économiques", "Variables médicales"]:
        card_content = [
            dbc.Collapse(
                card_content,
                id=f"collapsible-{item_name}",
                style={"padding": "0 0 1em 0"},
            )
        ]

    return dbc.Card([card_header] + card_content, color="dark", outline=True,)


def generate_qm(item):
    id_hash = df_variables[df_variables["nom_variable"] == item].index.values[0]
    question_mark = dbc.Badge("?", pill=True, color="light", id="badge-" + str(id_hash))

    return dbc.Col(question_mark, width=1, style={"padding": "5px"})


def generate_popovers():
    popovers = list()
    for i in range(df_variables.shape[0]):
        pp = dbc.Popover(
            [
                dbc.PopoverHeader(df_variables.iloc[i, :]["nom_variable"]),
                dbc.PopoverBody(df_variables.iloc[i, :]["explication"]),
            ],
            id=f"popover-{i}",
            target=f"badge-{i}",
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

    image_filename = "card_image_transparent.png"
    encoded_image = base64.b64encode(open(image_filename, "rb").read())

    card = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Img(
                                src="data:image/png;base64,{}".format(
                                    encoded_image.decode()
                                ),
                                alt="Mère et bébé",
                                width=130,
                            ),
                        ],
                        width=5,
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
                                style={
                                    "color": "#8ec63f",
                                    "font-weight": "bold",
                                },  # old color #00cc66
                            ),
                            html.P("de ces coûts sont liés au bébé"),
                        ],
                        width={"size": 6, "order": "last"},
                    ),
                ],
                no_gutters=True,
            )
        ],
        style={"vertical-align": "middle"},
    )

    return card


def millify(n):
    millnames = ["", " mille €", " millions d'€", " milliards d'€"]
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.1f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


def generate_form_naissances(bdd_naissances):
    form = dbc.Form(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Div("Choisir une échelle"),
                            html.I(
                                "(parmi : pays, région, département, ville, circonscription)"
                            ),
                        ],
                        style={"text-align": "center"},
                    )
                ],
                width=3,
            ),
            dbc.Col(
                [
                    dcc.Dropdown(
                        value=756662,
                        id="dd-echelle",
                        options=[
                            {
                                "label": r["Nom de l'échelon"],
                                "value": r["Nombre de naissances (2018)"],
                            }
                            for _, r in bdd_naissances.iterrows()
                        ],
                    ),
                ],
                width=4,
            ),
            dbc.Col([html.Div("")], width=1),
            dbc.FormGroup(
                [
                    dbc.Label("Nombre de naissances", className="mr-2"),
                    dbc.Input(type="number", min=0, step=1, id="nombre-naissances"),
                ],
            ),
        ],
        inline=True,
    )

    return html.Div(
        [
            html.H2("Première étape : choix du territoire", style={"color": "#8ec63f"}),
            form,
        ],
        style={"padding": "1em 0 1em 0"},
    )


def get_pitch():

    lien_article_site = (
        "http://alliance-psyperinat.org/2020/04/28/rapport-da-bauer-lse/"
    )
    lien_nhs = (
        "https://www.england.nhs.uk/2018/02/funding-boost-for-new-mums-mental-health/"
    )
    lien_nhs_2 = "https://www.england.nhs.uk/2016/02/fyfv-mh/"
    lien_nhs_3 = "https://www.england.nhs.uk/wp-content/uploads/2016/02/Mental-Health-Taskforce-FYFV-final.pdf"
    lien_govuk = (
        "https://www.gov.uk/government/news/prime-minister-pledges-a-revolution-in-mental-health-treatment"
    )



    pitch = html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "Le Royaume-Uni a compris dès 2014 l’importance d’investir sur les générations futures en finançant massivement la santé mentale périnatale. "
                    ),
                    html.Span("C’est notamment sous l’impulsion de l’article "),
                    html.A(
                        html.Span(
                            "The costs of perinatal mental health problems",
                            style={"font-style": "italic"},
                        ),
                        href=lien_article_site,
                        target="_blank",
                    ),
                    html.Span(
                        ", écrit par des chercheurs de la London School of Economics, que le gouvernement Cameron a investi plus de 300 millions de livres pour amorcer sa politique, et maintient désormais un financement annuel de 100 millions de livres "
                    ),
                    html.A(html.Span("[1]", style={"color": "black"}), href=lien_govuk, target="_blank"),
                    html.A(html.Span("[2]", style={"color": "black"}), href=lien_nhs, target="_blank"),
                    html.Span(
                        ". Pour mieux comprendre la nécessité de prendre en compte cet aspect de nos politiques de santé, et notamment dans une perspective d’investissement social, l’Alliance Francophone pour la Santé Mentale Périnatale a créé ce "
                    ),
                    html.Span("simulateur", style={"font-weight": "bold"}),
                    html.Span(
                        " qui réplique le modèle médico-économique de l’article Bauer "
                    ),
                    html.Span("et al.", style={"font-style": "italic"}),
                    html.Span(
                        " afin d’estimer le coût des maladies psychiatriques périnatales à toutes les échelles en France. "
                    ),
                    html.Span(
                        "Une partie significative de ces coûts peut être économisée par une politique ambitieuse de prévention."
                    ),
                ],
                style={"text-align": "justify", "font-size": "1.2em"},
            ),
        ],
        style={"border": "1px solid black", "padding": "1.5em 1.5em 1.5em 1.5em", "border-radius": "3px"},
    )
    return pitch
