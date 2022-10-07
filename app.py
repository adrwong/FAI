from distutils.log import INFO
from multiprocessing.sharedctypes import Value
from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash
import dash_bootstrap_components as dbc
import LoraLogger
import pandas as pd
import json
import plotly.io as pio

pio.templates.default = "plotly_dark"

logger = LoraLogger.logger(__name__, INFO)

# app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.VAPOR])
app = Dash(__name__, use_pages=True)

# read data
data_df = pd.read_excel('utils/FAI_results.xlsx')

# Demographic radio button options mappings
with open('utils/demo_mapping.json', 'r') as f:
    demo_mapping = json.load(f)
with open('utils/demo_groups.json', 'r') as f:
    demo_groups = json.load(f)
with open('utils/fin_mapping.json', 'r') as f:
    fin_mapping = json.load(f)
with open('utils/fin_groups.json', 'r') as f:
    fin_groups = json.load(f)


l_break = html.P(
    id='separate',
    children='|',
    style={
        'display': 'inline',
        'margin': '0 5px 0 -5px'
    }
)

app.layout = html.Div([
    html.H1(
        children='PolyU & AskLora FAI Result',
        style={
            'textAlign': 'center',
            'margin-top': '15px'
        }
    ),
    html.H5(
        children='Grouping Method',
        style={
            'textAlign': 'center',
            'margin-top': '15px'
        }
    ),
    dbc.RadioItems(
        id='gp_method',
        persistence=True,
        persistence_type='memory',
        options=[
            {
                "label": "Demographics",
                "value": "demo"
            },
            {
                "label": "Fintech Usage",
                "value": "fin"
            }
        ],
        value="demo",
        style={
            'textAlign': 'center',
        },
        labelStyle={
            'display': 'block',
        },
        inline=True
    ),
    html.Div(
        id='gp_details',
        children=[
            html.H5(
                id='gp_title_big',
                style={
                    'textAlign': 'center',
                    'margin-top': '15px'
                }
            ),
            dbc.RadioItems(
                id='demograph',
                persistence=True,
                persistence_type='memory',
                style={
                    'textAlign': 'center',
                },
                labelStyle={
                    'display': 'block',
                },
                inline=True,
                switch=True
            ),
            html.H5(
                id='gp_title',
                children=[
                    'Groups to show'
                ],
                style={
                    'textAlign': 'center',
                    'margin-top': '15px'
                }
            ),
            html.Div(
                children=[
                    html.Div(
                        id='group_options_bar',
                        children=[
                            html.Div(
                                id='group_options',
                                children=[
                                    dbc.Checklist(
                                        id='groups',
                                    ),
                                ],
                                style={
                                    'display': 'inline'
                                }
                            ),
                            html.Div(
                                id='group_options_traces',
                                children=[
                                    dbc.Checklist(
                                        id='bin_fin',
                                    ),
                                ],
                                style={
                                    'display': 'inline'
                                }
                            ),
                        ],
                        style={
                            'display': 'inline'
                        }
                    ),
                    dbc.Checklist(
                        id='percent',
                        persistence=True,
                        persistence_type='memory',
                        options=[
                            {'label': 'show percentage w.r.t. group', 'value': 'True'}],
                        value=[],
                        inline=True,
                        switch=True,
                        style={
                            'display': 'inline'
                        }
                    )
                ],
                style={
                    'textAlign': 'center',
                    'margin-top': '15px'
                }
            )
        ]
    ),
    html.Div(
        children=[
            html.Div(
                dcc.Link(
                    dbc.Button(page['name'].replace('_', ' ')),
                    href=page["relative_path"],
                    style={
                        'margin': '10px',
                    }
                ),
                style={
                    'display': 'inline-block'
                }
            )
            for page in dash.page_registry.values() if not page['name'].startswith('Segment')
        ] + [
            dbc.Button(
                "Download Raw Data Excel Sheet", id="download_xlsx_btn", style={'margin': '10px'}, color='info'
            ),
            dcc.Download(id="download_xlsx")
        ],
        style={
            'text-align': 'center',
            'padding-top': '20px',
            'padding-bottom': '20px',
        }
    ),
    html.Div(
        [
            html.Div(
                dcc.Link(
                    dbc.Button(page['name'].replace(
                        '_', ' '), color='danger'),
                    href=page["relative_path"],
                    style={
                        'margin': '10px',
                    }
                ),
                style={
                    'display': 'inline-block'
                }
            )
            for page in dash.page_registry.values() if page['name'].startswith('Segment')
        ],
        style={
            'text-align': 'center',
            'padding-top': '0px',
            'padding-bottom': '20px',
        }
    ),

    dash.page_container

],
    # style={'height': '100vh'}
)


@ app.callback(
    Output("download_xlsx", "data"),
    Input("download_xlsx_btn", "n_clicks"),
    prevent_initial_call=True
)
def down(n_clicks):
    return dcc.send_file("./utils/FAI_results.xlsx")


@ app.callback(

    Output(component_id='demograph', component_property='options'),
    Output(component_id='demograph', component_property='value'),
    Input(component_id='gp_method', component_property='value')
)
def update_group_options(method):
    if method == "demo":
        options = [demo_mapping[-1]] + demo_mapping[0:5]
        value = demo_mapping[-1]['value']
        return options, value
    if method == "fin":
        options = [demo_mapping[-1]] + fin_mapping[4:9]
        value = demo_mapping[-1]['value']
        return options, value


@ app.callback(
    Output(component_id='group_options', component_property='children'),
    Output(component_id='group_options_traces', component_property='children'),
    Output(component_id='gp_title', component_property='style'),
    Output(component_id='gp_title_big', component_property='children'),
    [
        Input(component_id='demograph', component_property='value'),
        Input(component_id='gp_method', component_property='value')
    ]
)
def update_groups(demo, gp_method):
    if gp_method == 'demo':
        groups = demo_groups
        mappings = demo_mapping
        gp_title = 'Demographic category to analyze'
    elif gp_method == 'fin':
        groups = fin_groups
        mappings = fin_mapping
        gp_title = 'Fintech usage to analyze'

    binary_user = dbc.Checklist(
        id='bin_fin',
        persistence=True,
        persistence_type='memory',
        options=[
            {'label': 'show binary users', 'value': 'False'}],
        value=[],
        inline=True,
        switch=True,
        style={
            'display': 'none'
        }
    )
    if demo == demo_mapping[-1]['value']:
        checkboxes = dbc.Checklist(
            id='groups',
            persistence=True,
            persistence_type='memory',
            options=demo_groups[demo][0:1],
            style={
                'textAlign': 'center',
                'display': 'none'
            },
            value=[bool(demo_groups[demo][0]['value'])],
            inline=True
        ),
        return checkboxes, binary_user, {'display': 'none'}, gp_title

    checkboxes = dbc.Checklist(
        id='groups',
        persistence=True,
        persistence_type='memory',
        options=groups[demo],
        style={
            'textAlign': 'center',
            'display': 'inline'
        },
        value=[l['value'] for l in groups[demo]],
        inline=True
    )

    if gp_method == 'fin':
        binary_user = dbc.Checklist(
            id='bin_fin',
            persistence=True,
            persistence_type='memory',
            options=[
                {'label': 'show binary users', 'value': 'False'}],
            value=[],
            inline=True,
            switch=True,
            style={
                'display': 'inline'
            }
        )
        return checkboxes, [l_break, binary_user], {'textAlign': 'center', 'margin-top': '15px'}, gp_title
    else:
        binary_user = dbc.Checklist(
            id='bin_fin',
            persistence=True,
            persistence_type='memory',
            options=[
                {'label': 'show binary users', 'value': 'False'}],
            value=[],
            inline=True,
            switch=True,
            style={
                'display': 'none'
            }
        )
        return checkboxes, [l_break, binary_user], {'textAlign': 'center', 'margin-top': '15px'}, gp_title


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8051)
