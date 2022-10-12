from enum import unique
from statistics import mean
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

mono_column = "Are you a Hong Kong resident?"

with open('utils/demo_mapping.json', 'r') as f:
    demo_mapping = json.load(f)
with open('utils/demo_groups.json', 'r') as f:
    demo_groups = json.load(f)
with open('utils/fin_mapping.json', 'r') as f:
    fin_mapping = json.load(f)
with open('utils/fin_groups.json', 'r') as f:
    fin_groups = json.load(f)
with open('utils/fin_bin_mapping.json', 'r') as f:
    fin_bin_mapping = json.load(f)
with open('utils/fin_bin_groups.json', 'r') as f:
    fin_bin_groups = json.load(f)


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
        Input(component_id='percent', component_property='value'),
        Input(component_id='gp_method', component_property='value'),
        Input(component_id='bin_fin', component_property='value'),
    ]
)
def update_graph(demo, gps, percent, gp_method, bin_fin):
    histnorm = None
    if percent:
        histnorm = 'percent'
    if gps == None or gps == []:
        return html.H3('Please select groups to show')
    charts = []

    if gp_method == "demo":
        groups = demo_groups
        mappings = demo_mapping
        temp_df_l = data_df.copy()

    elif gp_method == "fin" and bin_fin and demo != "Are you a Hong Kong resident?":
        groups = fin_bin_groups
        mappings = fin_bin_mapping
        temp_df_l = data_df.copy()
        temp_df_l = temp_df_l[temp_df_l[demo].isin(gps)]
        gps = ['User', 'Nonuser']
        temp_df_l[demo] = temp_df_l[demo].apply(
            lambda x: 'User' if x in ['User, Inactive', 'User, Active'] else 'Nonuser')

    elif gp_method == "fin":
        groups = fin_groups
        mappings = fin_mapping
        temp_df_l = data_df.copy()

    fai_df = []
    gp_overall = []

    for idx, col in enumerate(columns):
        if demo == col:
            continue
        temp_df = temp_df_l[[demo, col]].copy()
        temp_df = temp_df[temp_df[demo].isin(gps)]
        temp_df = temp_df.groupby(
            [demo, col], as_index=False).size()

        sort_dict = {
            col: [i['value'] for i in demo_groups["Segment Adoption"]],
            demo: [i['value'] for i in groups[demo]]
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
                demo: next(i for i in mappings if i['value'] == demo)[
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
        total_count = 0
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
            temp_df2_data.append([gp, idx1, idx2, idx3, ua + ui + ni + nu])
            total_count += ua + ui + ni + nu
        shortname = next(i for i in mappings if i['value'] == demo)[
            'label']
        temp2_cols = [shortname] + indices + ["count"]
        temp_df2 = pd.DataFrame(temp_df2_data, columns=temp2_cols)
        temp_df2 = temp_df2.set_index(shortname)
        temp_df2 = temp_df2.rename_axis('Index', axis=1)
        temp_df2 = temp_df2.T
        if demo == mono_column:
            temp_df2 = temp_df2.rename(columns=lambda x: next(
                i['label'] for i in mappings if i['value'] == col))
            temp_df2 = temp_df2.drop("count")
            fai_df.append(temp_df2)
        else:
            temp_df3 = temp_df2.copy()
            for c in temp_df3.columns.to_list():
                temp_df3[c] = temp_df3[c] * temp_df3[c].iloc[-1]
            temp_df3['all'] = temp_df3.sum(numeric_only=True, axis=1)
            temp_df3 = temp_df3[['all']]
            temp_df3['all'] = temp_df3['all'] / total_count
            temp_df2 = temp_df2.drop("count")
            temp_df3 = temp_df3.drop("count")

            fai_df.append(temp_df3)
            gp_overall.append(temp_df2)

        fig2 = px.imshow(
            temp_df2,
            x=temp_df2.columns,
            y=temp_df2.index,
            zmin=0,
            zmax=100,
            text_auto=True,
            color_continuous_scale=['#2EF9E2', '#fc003a'],
            title='<br>'.join(textwrap.wrap(next(i for i in mappings if i['value'] == col)[
                'label'], width=80))
        ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
        charts.append(dcc.Graph(
            id=f"fig_cal_{idx}",
            figure=fig2,
            style={'display': 'inline-block'}
        ))

    overall_fai = pd.concat(fai_df, axis=1)
    overall_fai['all'] = overall_fai.mean(numeric_only=True, axis=1)
    cols = overall_fai.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    overall_fai = overall_fai[cols]

    if demo != mono_column:
        extra_gp_overall = []
        for gp in gps:
            u_avg = sum([g.iloc[0][gp] for g in gp_overall]) / len(gp_overall)
            ui_avg = sum([g.iloc[1][gp] for g in gp_overall]) / len(gp_overall)
            ni_avg = sum([g.iloc[2][gp] for g in gp_overall]) / len(gp_overall)
            extra_gp_overall.append([gp, u_avg, ui_avg, ni_avg])
        shortname = next(i for i in mappings if i['value'] == demo)['label']
        gp_cols = [shortname] + indices
        gp_avg_df = pd.DataFrame(extra_gp_overall, columns=gp_cols)
        gp_avg_df = gp_avg_df.set_index(shortname)
        gp_avg_df = gp_avg_df.rename_axis('Index', axis=1)
        gp_avg_df = gp_avg_df.T
        overall_fai = pd.concat([overall_fai, gp_avg_df], axis=1)
    fig_all = px.imshow(
        overall_fai,
        x=overall_fai.columns,
        y=overall_fai.index,
        zmin=0,
        zmax=100,
        text_auto=True,
        color_continuous_scale=['#2EF9E2', '#fc003a'],
        title="Overall Financial Adoption Index"
    ).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    charts.insert(0, dcc.Graph(
        id=f"fig_overall",
        figure=fig_all,
        style={'display': 'inline-block'}
    ))
    return charts
