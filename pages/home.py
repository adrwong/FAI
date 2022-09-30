from turtle import st
import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(
    children=[
        html.H1(children='This is FAI results visualization Home page',
                style={
                    'textAlign': 'center',
                    'height': '100%',
                    'display': 'flex',
                    'flex-direction': 'column'
                }
                )

    ])
