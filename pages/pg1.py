import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name='Home')


layout = html.Div(
    [
        dbc.Row([
            dbc.Col(
                [
                    html.Img(src='assets/Bridges.jpg', width="1000", height="600")
                ],  
                width=12
            ),
        ])    
    ]
)
