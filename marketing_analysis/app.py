import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import dash.html as html
import dash.dcc as dcc
from dash.dash import Input, Output
from utils import *

data = pd.read_csv("data/Coffee_ready_data.csv")

app = dash.Dash(external_stylesheets=[dbc.themes.MORPH])

app.layout = html.Div(
    [dbc.Row(
        dbc.Col(
            html.Div([html.Br(), html.H1('Coffee Habits EDA')], style={'text-align':'center'}),
            width=6
            ),
        justify="center"
        ),
    dbc.Row(
        dbc.Col(
            html.Div(
                html.P(['''In this simple Dashboard are presented some interesting charts related to 
                    coffee habits around the world. The data is from ''',
                    html.A('Kaggle', href='https://www.kaggle.com/datasets/waqi786/worldwide-coffee-habits-dataset/data'),
                    ''' and it was cleaned and prepared for this example.''']),
                style={'text-align':'center'} 
                ),
            width=10
            ),
        justify="center", align="center"
        ),
    dbc.Row([
        dbc.Col(
                html.Div([html.P('Select a Year to explore'),
                          dcc.Slider(2000, 2023, 1, value=2023, id='year-slider',
                                    marks={i: f'{i}' for i in range(2000, 2024, 5)},
                                    tooltip={"always_visible": False,
                                            "style":{"color": "LightSteelBlue"}})
                            ], style={'text-align':"center"}
                        ),
                width={"size":5}
            ),
        dbc.Col(html.Div(dcc.Markdown("""Below, we can see how the **Cappuccino** is the most consumed coffee in 
                                last three years. Also, we see a downside trend in **Capitalization** since 2020. 
                                With a detailed data across months, it could be possible to see if the Covid-19 
                                pandemic is the main reason of it."""),
                        style={'text-align':'justify'}),
            width=5)
        ],
        align="center", justify="evenly"
        ),
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='type-by-country')), width=5),
        dbc.Col(html.Div(dcc.Graph(figure=get_coffee_consumed_global(data))), width=5)
    ], justify='evenly'),
    dbc.Row(
        dbc.Col([
            html.Br(),
            dcc.Markdown("Now, let's explore two chart related to the price of coffee")
            ], width=10),
        justify = "evenly"
        ),
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(figure=get_coffee_prices_global(data))), width=5),
        dbc.Col(html.Div(dcc.Graph(figure=get_mean_prices(data))), width=5)
    ],
    align="center", justify="evenly"),
    dbc.Row(
        dbc.Col(html.Div([
            html.Br(),
            dcc.Markdown("""Also, here you can visualize how the population is related to the price.
                         Below, there are two charts with coffee prices and consumption across the years taking into
                         account the top **N** and last **N** countries by population. Use the slider to you choose
                         different values of **N** and seehow it changes the plots.""")
            ], style={'text-align':'justify'}), width=10),
        justify = "evenly"
        ),
    dbc.Row(
        dbc.Col(
            html.Div([dcc.Slider(5, 15, 1, value=10, id='N-country-slider',
                                    marks={i: f'{i}' for i in range(5, 16, 3)},
                                    tooltip={"always_visible": False,
                                            "style":{"color": "LightSteelBlue"}})
                            ], style={'text-align':"center"}
                        ),          
            width = 8),
        justify='evenly'
    ),
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id = 'price-N')), width=5),
        dbc.Col(html.Div(dcc.Graph(id='consumption-N')), width=5)
    ],
    align="center", justify="evenly")
    ]
)


@app.callback(Output("type-by-country", "figure"),
              Input("year-slider", "value"))
def update_pie(year):
    tmp = data[data.Year == year]
    top5 = tmp[['Total Consumption', 'Country']].groupby('Country').sum().sort_values('Total Consumption', ascending=False).index[:5]
    fig = px.pie(tmp[tmp.Country.isin(top5)], 'Type', 'Total Consumption')
    fig.update_layout(title=f"Coffee Type distribution by consumption in<br>top 5 countries in {year}",
                      title_x=0.5)
    return fig

@app.callback([Output('price-N', 'figure'),
               Output('consumption-N', 'figure')],
               Input('N-country-slider', 'value'))
def update_N_countries(N):
    # Price across the years for more populated and least populated countries
    prices_top_botton = pd.DataFrame(columns=['Year', 'Top', 'Bottom'])
    for year in data.Year.unique():
        cbp = data[['Country', 'Population']][data.Year == year].groupby('Country').sum().sort_values('Population')
        top10 = data.Price[(data.Country.isin(cbp.index[-N:])) & (data.Year == year)].mean()
        bottom10 = data.Price[(data.Country.isin(cbp.index[:N])) & (data.Year == year)].mean()
        prices_top_botton.loc[len(prices_top_botton), :] = [year, top10, bottom10]
    
    # Consumption across the years for more populated and least populated countries
    cons_top_botton = pd.DataFrame(columns=['Year', 'Top', 'Bottom'])
    for year in data.Year.unique():
        cbc = data[['Country', 'Population']][data.Year == year].groupby('Country').sum().sort_values('Population')
        top10 = data.Consumption[(data.Country.isin(cbc.index[-N:])) & (data.Year == year)].mean()
        bottom10 = data.Consumption[(data.Country.isin(cbc.index[:N])) & (data.Year == year)].mean()
        cons_top_botton.loc[len(cons_top_botton), :] = [year, top10, bottom10]

    fig1 = go.Figure(go.Scatter(x = prices_top_botton.Year, y = prices_top_botton.Top, 
                            name=f'Top {N}', mode='lines'))
    fig1.add_trace(go.Scatter(x = prices_top_botton.Year, y = prices_top_botton.Bottom, 
                            name=f'Last {N}', mode='lines'))
    fig2 = go.Figure(go.Scatter(x = cons_top_botton.Year, y = cons_top_botton.Top, 
                           name=f'Top {N}', mode='lines'))
    fig2.add_trace(go.Scatter(x = cons_top_botton.Year, y = cons_top_botton.Bottom, 
                         name=f'Last {N}', mode='lines'))
    
    fig2.update_layout(title='Consumption across the years by population',
                       title_x=0.5)
    fig1.update_layout(title='Price across the years by population',
                       title_x=0.5)
    fig1.update_yaxes(title='Price (USD/Kg)')
    fig2.update_yaxes(title="Consumption (Kg/Year)")

    return fig1, fig2

if __name__ == "__main__":
    app.run_server(debug=False)