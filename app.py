import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from itertools import chain
import pandas as pd

# DASH AND APP SETTINGS
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# CSS SETTINGS
eq_width = {"width": "20%", "text-align": "center"}

tt = {"always_visible": False, "placement": "topLeft"}

# VARIABLES
global df_variables

df_variables = pd.read_csv(
    "variables_bauer - Feuille 1.csv"
)



def generate_random_df():
    df = pd.DataFrame(data={"Maladie": ["Dépression", "Anxiété", "Psychose"]})
    df["Coût total"] = np.random.randint(0, int(2e10)) / np.arange(1, 4)
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


def make_row(it):
    return (
        dbc.Row(
            [dbc.Col(html.Label(it)), dbc.Col(question_mark)],
            form=False,
            justify="around",
        ),
    )


def generate_qm(item):
    id_hash = df_variables[df_variables['nom_variable']==item].index.values[0]
    question_mark = dbc.Badge("?", pill=True, color="light", id="badge_" + str(id_hash))

    return dbc.Col(question_mark, width=1)


def make_group(title, items):
    """items est un dict sous forme : key = nom var ; value = widget"""
    return dbc.Card(
        [dbc.CardHeader(title),]
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
                    row.mini: {"label": f"{row.mini} {row.unit}"},
                    row.val: {"label": f"{row.val} {row.unit}"},
                    row.maxi: {"label": f"{row.maxi} {row.unit}"},
                },
            ),
            dbc.Popover(
                        [
                            dbc.PopoverHeader("Header"),
                            dbc.PopoverBody(f"{row.explication}"),
                        ],
                        id="popover-" + " ".join(["qm", row["nom_variable"].lower()]),
                        target=" ".join(["qm", row["nom_variable"].lower()]),
                        is_open=False,
                    )

            #dbc.Tooltip(row.explication, target=, autohide=False),
        ]
        for _, row in df_categ.iterrows()
    }

    return dict_items

def generate_popovers():
    popovers = list()
    for i in range(df_variables.shape[0]):
        pp = dbc.Popover(
                            [
                                dbc.PopoverHeader("Header"),
                                dbc.PopoverBody(df_variables.iloc[i, :]['explication']),
                            ],
                            id=f"popover-{i}",
                            target=f"badge_{i}",
                            is_open=False,
                        )
        popovers.append(pp)
    return popovers


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
    ]
)


button_generate = dbc.Button(
    "Générer l'estimation !", color="primary", block=True, id="button-generate",
)

df_final = generate_random_df()

# BAR CHART
idxs = list(df_final.index[:])
fig = go.Figure(
    data=[
        go.Bar(
            name="Part Bébés", x=idxs, y=df_final["Part Bébés"].values[:], text=idxs
        ),
        go.Bar(
            name="Part Mères", x=idxs, y=df_final["Part Mères"].values[:], text=idxs
        ),
    ]
)
fig.update_layout(
    barmode="stack", title="Répartition des coûts entre la mère et le bébé (en %)"
)

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

charts_coll = dbc.Collapse(
    [
        # dcc.Graph(id="example-graph-2", figure=fig),
        dcc.Graph(id="example-graph-pie", figure=pie_maladies),
    ],
    id="collapsed-graphs",
)

app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Estimer le coût des maladies psypérinatales en France"),
        tabs,
        html.Hr(),
        button_generate,
        html.Hr(),
        charts_coll,
        html.Hr(),
    ] + generate_popovers()
)


@app.callback(
    Output("collapsed-graphs", "is_open"),
    [Input("button-generate", "n_clicks")],
    [State("collapsed-graphs", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

for i in range(df_variables.shape[0]):
    app.callback(
        Output(f"popover-{i}", "is_open"),
        [Input(f"badge_{i}", "n_clicks")],
        [State(f"popover-{i}", "is_open")],
    )(toggle_popover)


if __name__ == "__main__":
    app.run_server(
        debug=True, 
        #port=8890,  # remove line if heroku
    )
