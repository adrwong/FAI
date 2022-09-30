import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import LoraLogger
from distutils.log import INFO
import json
import textwrap

dash.register_page(__name__, path='/mobile_payments')
logger = LoraLogger.logger(__name__, INFO)
data_df = pd.read_excel('../utils/FAI_results.xlsx')

segment_column = '9. Have you ever used mobile payment?'

with open('utils/demo_mapping.json', 'r') as f:
    demo_mapping = json.load(f)
with open('utils/demo_groups.json', 'r') as f:
    demo_groups = json.load(f)

layout = html.Div(children=[
    html.H5(
        children='Mobile Payments',
        style={
            'textAlign': 'center',
            'margin-top': '15px'
        }
    ),
    dcc.Loading(
        id="mb-loading",
        children=[html.Div(id='fig_mb', style={
                           'textAlign': 'center', 'height': '100vh'})],
        type="cube",
        color="#E939B8"
    )
])


@callback(
    Output(component_id='fig_mb', component_property='children'),
    [
        Input(component_id='demograph', component_property='value'),
        Input(component_id='groups', component_property='value'),
        Input(component_id='percent', component_property='value')
    ]
)
def update_graph(demo, gps, percent):
    histnorm = None
    if percent:
        histnorm = 'percent'
    if gps == None or gps == []:
        return html.H3('Please select groups to show')
    charts = []
    temp_df = data_df[data_df[demo].isin(gps)]
    temp_df = temp_df[[segment_column]].copy()
    temp_df = temp_df.groupby([segment_column], as_index=True).size()
    try:
        ua = temp_df['User, Active']
    except:
        ua = 0
    try:
        ui = temp_df['User, Inactive']
    except:
        ui = 0
    try:
        ni = temp_df['Nonuser, Interesed']
    except:
        ni = 0
    try:
        nu = temp_df['Nonuser, Uninteresed']
    except:
        nu = 0

    adoption_matrix = [[ua, ui], [ni, nu]]
    fig2 = px.imshow(
        adoption_matrix,
        x=['Interested', 'Uninterested'],
        y=['User', 'Nonuser'],
        zmin=0,
        text_auto=True,
        color_continuous_scale=['#2EF9E2', '#fc003a'],
        title='<br>'.join(textwrap.wrap(next(i for i in demo_mapping if i['value'] == segment_column)[
            'label'] + ' adoption count (sum of selected groups)', width=80))
    ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    charts.append(dcc.Graph(
        id=f"adopt_overall",
        figure=fig2,
        style={'display': 'inline-block'}
    ))

    column_idx = data_df.columns.get_loc(segment_column)
    columns = data_df.columns.values.tolist()[column_idx+1:column_idx+6]
    for idx, col in enumerate(columns):

        temp_df = data_df[[demo, col]].copy()
        temp_df = temp_df[temp_df[demo].isin(gps)]
        temp_df = temp_df.groupby(
            [demo, col], as_index=False).size()

        sort_dict = {
            col: ['1', '2', '3', '4', '5'],
            demo: [i['value'] for i in demo_groups[demo]]
        }
        fig1 = px.histogram(
            temp_df,
            x=col,
            y='size',
            color=demo,
            histnorm=histnorm,
            barmode="group",
            labels={
                col: next(i for i in demo_mapping if i['value'] == col)[
                    'label'],
                'sum of size': 'count',
                demo: next(i for i in demo_mapping if i['value'] == demo)[
                    'label']
            },
            category_orders=sort_dict,
            title='<br>'.join(textwrap.wrap(col, width=80))
        ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', xaxis=dict(type='category'))
        charts.append(dcc.Graph(
            id=f"fig{idx}",
            figure=fig1,
            style={'display': 'inline-block'}
        ))

    return charts
