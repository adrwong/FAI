from enum import unique
from turtle import width
import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import LoraLogger
from distutils.log import INFO
import json
import textwrap

dash.register_page(__name__, path='/adoption_indices')
logger = LoraLogger.logger(__name__, INFO)
data_df = pd.read_excel('../utils/FAI_results.xlsx')

columns = [
    "7. Do you have a virtual bank account?",
    "9. Have you ever used mobile payment?",
    "11. Do you have an online stock brokers platform account?",
    "13. Have you ever used digital insurance?",
    "15. Have you ever traded cryptocurrency?"
]

with open('utils/demo_mapping.json', 'r') as f:
    demo_mapping = json.load(f)
with open('utils/demo_groups.json', 'r') as f:
    demo_groups = json.load(f)

layout = html.Div(children=[
    html.H5(
        children='Fintech Adoption Index',
        style={
            'textAlign': 'center',
            'margin-top': '15px'
        }
    ),
    dcc.Loading(
        id="adopt-loading",
        children=[html.Div(id='fig_adopt', style={
                           'textAlign': 'center', 'height': '100vh'})],
        type="cube",
        color="#E939B8"
    )
])


@callback(
    Output(component_id='fig_adopt', component_property='children'),
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

    for idx, col in enumerate(columns):

        temp_df = data_df[[demo, col]].copy()
        temp_df = temp_df[temp_df[demo].isin(gps)]

        temp_df = temp_df.groupby(
            [demo, col], as_index=False).size()
        sort_dict = {
            col: [i['value'] for i in demo_groups["Segment Adoption"]],
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
        ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
        charts.append(dcc.Graph(
            id=f"fig{idx}",
            figure=fig1,
            style={'display': 'inline-block'}
        ))
        indices = ['Adoption Index', 'Active User Index',
                   'Interested Nonuser Index']
        temp_df2_data = []
        for gp in gps:
            try:
                ua = temp_df.loc[temp_df[demo] == gp].loc[temp_df[col]
                                                          == 'User, Active', 'size'].iloc[0]
            except:
                ua = 0
            try:
                ui = temp_df.loc[temp_df[demo] == gp].loc[temp_df[col]
                                                          == 'User, Inactive', 'size'].iloc[0]
            except:
                ui = 0
            try:
                ni = temp_df.loc[temp_df[demo] == gp].loc[temp_df[col]
                                                          == 'Nonuser, Interesed', 'size'].iloc[0]
            except:
                ni = 0
            try:
                nu = temp_df.loc[temp_df[demo] == gp].loc[temp_df[col]
                                                          == 'Nonuser, Uninteresed', 'size'].iloc[0]
            except:
                nu = 0
            if (ua + ui + ni + nu) == 0:
                idx1 = 0
            else:
                idx1 = (ua + ui) * 100 / (ua + ui + ni + nu)
            if (ua + ui) == 0:
                idx2 = 0
            else:
                idx2 = ua * 100 / (ua + ui)
            if (ni + nu) == 0:
                idx3 = 0
            else:
                idx3 = ni * 100 / (ni + nu)
            temp_df2_data.append([gp, idx1, idx2, idx3])
        shortname = next(i for i in demo_mapping if i['value'] == demo)[
            'label']
        temp2_cols = [shortname] + indices
        temp_df2 = pd.DataFrame(temp_df2_data, columns=temp2_cols)
        temp_df2 = temp_df2.set_index(shortname)
        temp_df2 = temp_df2.rename_axis('Index', axis=1)
        temp_df2 = temp_df2.T
        fig2 = px.imshow(
            temp_df2,
            x=temp_df2.columns,
            y=temp_df2.index,
            zmin=0,
            zmax=100,
            text_auto=True,
            color_continuous_scale=['#2EF9E2', '#fc003a'],
            title='<br>'.join(textwrap.wrap(next(i for i in demo_mapping if i['value'] == col)[
                'label'], width=80))
        ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
        charts.append(dcc.Graph(
            id=f"fig_cal_{idx}",
            figure=fig2,
            style={'display': 'inline-block'}
        ))

    return charts
