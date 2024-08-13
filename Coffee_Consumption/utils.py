import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def get_coffee_consumed_global(data):
    """Most dominant coffee globally by market value and year"""
    ## Filter data and sum it
    mkv = data[['Year', 'Price', 'Total Consumption', 'Type']].groupby(["Year",'Type']).sum()
    # Get total market revenue
    mkv['Capitalization'] = mkv.Price * mkv['Total Consumption']
    # Drop data and Unstack it
    mkv = mkv.drop(['Price', 'Total Consumption'], axis=1).unstack()['Capitalization']
    # Resamble df to have most consumed coffee type by year
    mcc = pd.DataFrame(columns = ['Type', 'Capitalization'], index=mkv.index)
    for i, m in enumerate(mkv.max(axis=1)):
        mcc.loc[mkv.index[i], ["Type", 'Capitalization']] = [mkv.columns[mkv.iloc[i] == m].values[0], m]
    mcc.reset_index(inplace=True)
    # Plot trends
    fig = go.Figure()
    for t in mcc.Type.unique():
        fig.add_trace(go.Bar(x=mcc.Year[mcc.Type == t], y=mcc.Capitalization[mcc.Type == t], name=t))

    fig.update_layout(title="Most Consumed Coffee Globally by Capitalization",
                      title_x=0.5)
    fig.update_yaxes(range=(5000000, 12000000))
    return fig

def get_coffee_prices_global(data):
    ## Filter data and get the mean
    mkv = data[['Year', 'Price', 'Type']].groupby(["Year",'Type']).mean()
    mkv = mkv.unstack()['Price']
    # Resamble df to have most expensive coffee type by year
    mec = pd.DataFrame(columns = ['Type', 'Price'], index=mkv.index)
    for i, m in enumerate(mkv.max(axis=1)):
        mec.loc[mkv.index[i], ["Type", 'Price']] = [mkv.columns[mkv.iloc[i] == m].values[0], m]
    mec.reset_index(inplace=True)
    mec.Price = mec.Price.astype('float64')
    # Plot trends
    fig = go.Figure()
    for t in mec.Type.unique():
        fig.add_trace(go.Bar(x=mec.Year[mec.Type == t], y = mec.Price[mec.Type == t], name=t))

    fig.update_layout(title="Most Expensive Coffee Globally acrross the years",
                      title_x=0.5)
    fig.update_yaxes(range=(9.6, 10.4))
    fig.update_yaxes(title="Coffee Price (USD/Kg)")
    return fig

def get_mean_prices(data):
    # General price of coffee across the years
    mpy = data[['Year', 'Price']].groupby('Year').mean()
    fig = go.Figure(go.Scatter(x = mpy.index, y = mpy.Price, mode='lines'))
    fig.update_layout(title='Mean price of Coffee across the years',
                      title_x=0.5)
    fig.update_yaxes(title="Coffee Price (USD/Kg)")    
    return fig