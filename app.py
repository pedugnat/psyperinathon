import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from itertools import chain

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

eq_width = {"width": "20%",
            "text-align": "center"}

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 2!", className="card-text"),
            dbc.Button("Don't click here", color="danger"),
        ]
    ),
    className="mt-3",
)



def make_group(title, items):
    """items est un dict sous forme : key = nom var ; value = widget"""
    return dbc.Card(
            [
                dbc.CardHeader(title),

            ] + list(chain(*[[html.Label(it), items[it]] for it in items])),
            color="dark", outline=True
        )
# DEPRESSION
items_depression_mere = {"Coût pour le service public de la dépression de la mère": dcc.Slider(min=0, max=100, value=50, step=1)}
items_depression_mere = {"Coût pour le service public de la dépression de la mère": dcc.Slider(min=0, max=100, value=50, step=1)}



# ANXIETE
items_anxiete_mere = {"Coût pour le service public de l'anxiété de la mère": dcc.Slider(min=0, max=100, value=50, step=1),
                      "Coût pour la justice de l'anxiété de la mère": dcc.Slider(min=0, max=100, value=50, step=1)}


# PSYCHOSE
items_psychose_mere = {"Coût pour le service public de la psychose de la mère": dcc.Slider(min=0, max=100, value=50, step=1),
                      "Coût pour la justice de la psychose de la mère": dcc.Slider(min=0, max=100, value=50, step=1)}

# VARIABLES MEDICALES
items_medical = {"Prévalence de la dépression": dcc.Slider(min=0, max=25, value=10, step=0.5, marks={0: {'label': '0 %'},
                                                                                                   10: {'label': '10 %'},
                                                                                                   25: {'label': '25 %'}}),
                 "Prévalence de l'anxiété": dcc.Slider(min=0, max=10, value=3, step=0.1, marks={0: {'label': '0 %'},
                                                                                               3: {'label': '3 %'},
                                                                                               10: {'label': '10 %'}}),
                 "Prévalence de la psychose": dcc.Slider(min=0, max=3, value=0.2, step=0.01, marks={0: {'label': '0 %'},
                                                                                                   0.2: {'label': '0.2 %'},
                                                                                                   3: {'label': '3 %'}}),
                 "Nombre de naissances en France": dcc.Slider(min=0, max=1000, value=800, step=1, marks={0: {'label': '0 k naissances'},
                                                                                                       800: {'label': '800 k naissances'},
                                                                                                       1000: {'label': '1000 k naissances'}}),
                }

# VARIABLES ECONOMIQUES
items_economique = {"Valeur d'une année de QALY": dcc.Slider(min=0, max=25, value=10, step=0.5, marks={0: {'label': '0 k€'},
                                                                                                       10: {'label': '10 k€'},
                                                                                                       25: {'label': '25 k€'}}),
                     "Prix d'une vie": dcc.Slider(min=0, max=10, value=3, step=0.1, marks={0: {'label': '0 M€'},
                                                                                           3: {'label': '3 M€'},
                                                                                           10: {'label': '10 M€'}}),
                     "Revenu moyen hebdomadaire d'une femme": dcc.Slider(min=0, max=1000, value=450, step=10, marks={0: {'label': '0 €/semaine'},
                                                                                                                       450: {'label': '450 €/semaine'},
                                                                                                                       1000: {'label': '1000 €/semaine'}}),
                     "Part des femmes employées avant la naissance": dcc.Slider(min=0, max=100, value=74, step=1, marks={0: {'label': '0 %'},
                                                                                                                       74: {'label': '74 %'},
                                                                                                                       100: {'label': '100 %'}}),
                     "Part des femmes reprenant un emploi après la naissance": dcc.Slider(min=0, max=100, value=75, step=1, marks={0: {'label': '0 %'},
                                                                                                                                   75: {'label': '75 %'},
                                                                                                                                   100: {'label': '100 %'}}),
                     "Part des femmes reprenant à plein temps": dcc.Slider(min=0, max=100, value=20, step=1, marks={0: {'label': '0 %'},
                                                                                                                   20: {'label': '20 %'},
                                                                                                                   100: {'label': '100 %'}}),
                }


tabs = dbc.Tabs(
    [
        dbc.Tab([make_group('Depression Mère', items_depression_mere),
                 make_group('Depression Bébé', items_depression_mere)], 
                    label="Dépression", tab_style=eq_width),
        dbc.Tab([make_group('Anxiété Mère', items_anxiete_mere),
                 make_group('Anxiété Bébé', items_anxiete_mere)], 
                    label="Anxiété", tab_style=eq_width),
        dbc.Tab([make_group('Psychose Mère', items_psychose_mere),
                 make_group('Psychose Bébé', items_psychose_mere)], 
                    label="Psychose", tab_style=eq_width),
        dbc.Tab(make_group('Variables médicales', items_medical), 
                    label="Variables médicales", tab_style=eq_width),        
        dbc.Tab(make_group('Variables économiques', items_economique), 
                    label="Variables économiques", tab_style=eq_width),

    ]
)

button_generate = dbc.Button(
                            "Génération l'estimation !",
                            color="primary",
                            block=True,
                            id="button",
        )

app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Estimer le coût des maladies psypérinatales en France"),
        html.Hr(),
        tabs,
        html.Hr(),
        button_generate,
    ]
)



if __name__ == '__main__':
    app.run_server(debug=True)

