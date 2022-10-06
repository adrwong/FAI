import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import LoraLogger
from distutils.log import INFO
import json
import textwrap

dash.register_page(__name__, path='/demographics')

logger = LoraLogger.logger(__name__, INFO)
data_df = pd.read_excel('../utils/FAI_results.xlsx')
all_demo = "Are you a Hong Kong resident?"


with open('utils/demo_mapping.json', 'r') as f:
    demo_mapping = json.load(f)
with open('utils/demo_groups.json', 'r') as f:
    demo_groups = json.load(f)

title_5th = demo_mapping[5]['value']
data_df[title_5th] = data_df[title_5th].apply(lambda x: x[1:-1].split(','))

layout = html.Div(children=[
    html.H5(
        children='Demographic Stats',
        style={
            'textAlign': 'center',
            'margin-top': '15px'
        }
    ),
    dcc.Loading(
        id="demo-loading",
        children=[html.Div(id='fig_demo', style={
                           'textAlign': 'center', 'height': '100vh'})],
        type="cube",
        color="#E939B8"
    )
])


@callback(
    Output(component_id='fig_demo', component_property='children'),
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
    logger.info(demo)
    logger.info(gps)
    if gps == None or gps == []:
        return html.H3('Please select groups to show')
    columns = data_df.columns.values.tolist()[1:6]
    if demo in columns:
        columns.remove(demo)
    charts = []
    temp_df = data_df[[demo]].copy()
    temp_df = temp_df[temp_df[demo].isin(gps)]
    temp_df = temp_df.groupby([demo], as_index=False).size()
    if demo != all_demo:
        fig0 = px.pie(
            temp_df,
            values='size',
            names=demo,
            labels={
                demo: next(i for i in demo_mapping if i['value'] == demo)[
                    'label']
            },
            category_orders={
                demo: [i['value'] for i in demo_groups[demo]]
            },
            title=f"Groups Distribution",
        ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
        charts.append(dcc.Graph(
            id=f"fig_custom_0",
            figure=fig0,
            style={'display': 'inline-block'}
        ))

    for idx, col in enumerate(columns):

        temp_df = data_df[[demo, col]].copy()
        temp_df = temp_df[temp_df[demo].isin(gps)]
        temp_df = temp_df.groupby(
            [demo, col], as_index=False).size()
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
            category_orders={
                col: [i['value'] for i in demo_groups[col]],
                demo: [i['value'] for i in demo_groups[demo]]
            },
            title='<br>'.join(textwrap.wrap(col, width=80))
        ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
        charts.append(dcc.Graph(
            id=f"fig{idx}",
            figure=fig1,
            style={'display': 'inline-block'}
        ))

    temp_df = data_df[[demo, title_5th]].copy()
    temp_df = temp_df[temp_df[demo].isin(gps)]
    temp_df = temp_df.explode(title_5th)
    temp_df = temp_df.groupby(
        [demo, title_5th], as_index=False).size()
    fig2 = px.histogram(
        temp_df,
        x=title_5th,
        y='size',
        color=demo,
        histnorm=histnorm,
        barmode="group",
        labels={
            title_5th: demo_mapping[5]['label'],
            'sum of size': 'count',
            demo: next(i for i in demo_mapping if i['value'] == demo)[
                'label']
        },
        category_orders={
            demo: [i['value'] for i in demo_groups[demo]]
        },
        title='<br>'.join(textwrap.wrap(title_5th, width=80))
    ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    charts.append(dcc.Graph(
        id=f"fig_custom_2",
        figure=fig2,
        style={'display': 'inline-block'}
    ))

    col = demo_mapping[6]['value']
    temp_df = data_df[[demo, col]].copy()
    temp_df = temp_df[temp_df[demo].isin(gps)]
    temp_df = temp_df.groupby(
        [demo, col], as_index=False).size()
    fig2 = px.histogram(
        temp_df,
        x=col,
        y='size',
        color=demo,
        barmode="group",
        labels={
            col: demo_mapping[6]['label'],
            'sum of size': 'count',
            demo: next(i for i in demo_mapping if i['value'] == demo)[
                'label']
        },
        category_orders={
            col: [i['value'] for i in demo_groups[col]],
            demo: [i['value'] for i in demo_groups[demo]]
        },
        title='<br>'.join(textwrap.wrap(col, width=80))
    ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    charts.append(dcc.Graph(
        id=f"fig_custom_3",
        figure=fig2,
        style={'display': 'inline-block'}
    ))

    return charts
