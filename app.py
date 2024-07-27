import numpy as np
import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import zipfile
import requests
import io


def read_csv_from_url_zip(url, csv_file_name):
    # Download the zip file from the URL
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Read the zip file from the response content
    zip_file = io.BytesIO(response.content)

    # Extract and read the CSV file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        with zip_ref.open(csv_file_name) as csv_file:
            df = pd.read_csv(csv_file)
            return df

# Usage
url = 'https://raw.githubusercontent.com/twogunzpadre/Incidents/main/WarConflicts.zip'  # Correct URL to the raw zip file
csv_file_name = 'WarConflicts.csv'



# Read the CSV file from the zip archive
df = read_csv_from_url_zip(url, csv_file_name)
df['country'] = df['country'].astype(str)
sorted_years = sorted(df['year'].unique())
df = df.dropna()


# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        # Selection 1
        html.H1("Yearly Statistics for Nations in Conflicts",
                style={'textAlign': 'left', 'color': '#503D36', 'font-size': 24}),
        html.Div([
            html.Label("Select a country"),
            dcc.Dropdown(
                id='country-drop',
                options=[{'label': 'All Countries', 'value': 'All Countries'}] + 
                        [{'label': country, 'value': country} for country in df['country'].unique()],
                value='All Countries',
                placeholder='Select a country',
                style={'textAlign': 'left', 'width': '40%', 'padding': '3px', 'font-size': '20px'}
            )
        ]),
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex'}),
    ], style={'width': '60%', 'float': 'left'}),
#----------------------------------------------------------------------------------------------------------------------------------------------
    html.Div([
        html.H2("Count of Conflicts for Selected Year",
                style={'textAlign': 'left', 'color': '#503D36', 'font-size': 24}),
        html.Div([
            html.Label("Select A Year"),
            dcc.Dropdown(
                id='year-drop',
                options=[{'label': 'All Years', 'value': 'All Years'}] + 
                        [{'label': year, 'value': year} for year in sorted(df['year'].unique())],
                value='All Years',
                placeholder='Select a Year',
                style={'textAlign': 'left', 'width': '100%', 'padding': '3px', 'font-size': '20px'})
        ]),
        html.Div(id='output-container2', className='chart-grid', style={'display': 'flex'})
    ], style={'width': '40%', 'float': 'right'}),
#----------------------------------------------------------------------------------------------------------------------------------------------
    html.Div([
        html.H3("Total Deaths and Types of Violence for Selected Country",
                style={'textAlign': 'left', 'color': '#503D36', 'font-size': 24}),
        html.Div(id='output-container3', className='chart-grid', style={'display': 'flex'})
    ], style={'width': '60%', 'float': 'left'}),
#----------------------------------------------------------------------------------------------------------------------------------------------

    html.Div([
        html.H4("Total Deaths for Conflicts in selected country, year",
                style={'textAlign': 'left', 'color': '#503D36', 'font-size': 24}),
        html.Div(id='output-container4', className='chart-grid', style={'display': 'flex'})
    ], style={'width': '40%', 'float': 'right'}),
#;------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
    html.Div([
        html.H5("Types of Death per region in Selected Country and year",
                style={'textAlign': 'left', 'color': '#503D36', 'font-size': 24}),
        html.Div(id='output-container5', className='chart-grid', style={'display': 'flex'})
    ], style={'width': '60%', 'float': 'left'}),
#;------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
html.Div([
          html.H6("Types of Death per Country (Map Visualization)",
                style={'textAlign': 'left', 'color': '#503D36', 'font-size': 24}),
        dcc.RadioItems(
            id='deaths-type-radio',
            options=[
                {'label': 'All Sides', 'value': 'All Sides'},
                {'label': 'Deaths Side A', 'value': 'deaths_a'},
                {'label': 'Deaths Side B', 'value': 'deaths_b'},
                {'label': 'Deaths Unknown', 'value': 'deaths_unknown'},
                {'label': 'Civilians Deaths', 'value': 'deaths_civilians'}
            ],
            value='All Sides',
            labelStyle={'display': 'inline-block'}
        ),
        html.Div(id='output-container6', className='chart-grid', style={'display': 'flex'})
    ], style={'width': '40%', 'float': 'left'})
], style={'display': 'flex', 'flex-wrap': 'wrap'})
#------------------------------------------------------------------------------------------------------------------------------------------------------
# TASK 2.4: Creating Callbacks
@app.callback(
    Output(component_id='output-container', component_property='children'),
    Input(component_id='country-drop', component_property='value'))
def update_input_container(selected_country):
    if selected_country == 'All Countries':
        dfcountry = df.copy()
    else:
        dfcountry = df[df['country'] == selected_country]
    dfcountry = dfcountry['year'].value_counts().to_frame().reset_index()
    dfcountry.columns = ['Year', 'Count']
    dfcountry = dfcountry.sort_values(by="Year")

    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=dfcountry['Year'], y=dfcountry['Count']))
    bar_fig.update_layout(title="Counts of Conflicts by Year for " + selected_country)

    R_chart1 = dcc.Graph(figure=bar_fig)
    return [html.Div(className='chart-item', children=[R_chart1], style={'display': 'flex'})]



#;------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




@app.callback(
    Output(component_id='output-container2', component_property='children'),
    Input(component_id='year-drop', component_property='value'))
def update_input_container2(selected_year):
    if selected_year == 'All Years':
        dfyear = df.copy()
        dfyear = dfyear.sort_values(by='year')
    else:
        dfyear = df[df['year'] == selected_year]
        dfyear = dfyear.sort_values(by='year')

    conflicts = dfyear['conflict_name'].value_counts().to_frame().reset_index()
    conflicts.columns = ['conflict_name', 'count']
    conflicts = conflicts.sort_values(by='count', ascending=False)
    conflicts = conflicts.head(15)

    R_chart2 = dcc.Graph(
        figure=px.bar(conflicts, x='conflict_name', y='count',
                      title="Counts of Conflicts for Year " + str(selected_year))
    )
    return [html.Div(className='chart-item', children=[R_chart2], style={'display': 'flex'})]


#;------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



@app.callback(
    Output(component_id='output-container3', component_property='children'),
    Input(component_id='country-drop', component_property='value'),
    Input(component_id='year-drop', component_property='value'))
def update_input_container3(selected_country, selected_year):
    if selected_year == 'All Years':
        df_filtered = df[df['country'] == selected_country] if selected_country != 'All Countries' else df
    else:
        df_filtered = df[(df['country'] == selected_country) & (df['year'] == selected_year)] if selected_country != 'All Countries' else df[df['year'] == selected_year]

    tov = df_filtered.groupby('type_of_violence')['deaths_total'].sum().reset_index()

    

    bar3_fig = go.Figure()
    bar3_fig.add_trace(go.Bar(x=tov['type_of_violence'], y=tov['deaths_total'], text=tov['deaths_total'], textposition='outside'))

    bar3_fig.update_layout(barmode='stack', title='Sides and Types of Violence for ' + selected_country + ' in ' + str(selected_year), xaxis_title='Type of Violence', yaxis_title='Total Deaths')

    R_chart3 = dcc.Graph(figure=bar3_fig)
    return [html.Div(className='chart-item', children=[R_chart3], style={'display': 'flex'})]
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output(component_id='output-container4', component_property='children'),
    Input(component_id='country-drop', component_property='value'),
    Input(component_id='year-drop', component_property='value'))
def update_input_container3(selected_country, selected_year):
    if selected_year == 'All Years':
        df_filtered = df[df['country'] == selected_country] if selected_country != 'All Countries' else df
    else:
        df_filtered = df[(df['country'] == selected_country) & (df['year'] == selected_year)] if selected_country != 'All Countries' else df[df['year'] == selected_year]

    dpc = df_filtered.groupby('conflict_name')['deaths_total'].sum().reset_index()
    dpc = dpc.sort_values(by = 'deaths_total', ascending = False)
    dpc = dpc.head(20)

    

    bar4_fig = go.Figure()
    bar4_fig.add_trace(go.Bar(x=dpc['conflict_name'], y=dpc['deaths_total'], text=dpc['deaths_total'], textposition='outside'))
    bar4_fig.update_layout(title='Count of Deaths for conflicts for ' + selected_country + ' in ' + str(selected_year), xaxis_title='Conflict Name', yaxis_title='Total Deaths')
    R_chart4 = dcc.Graph(figure=bar4_fig)
    return [html.Div(className='chart-item', children=[R_chart4], style={'display': 'flex'})]
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output(component_id='output-container5', component_property='children'),
    Input(component_id='country-drop', component_property='value'),
    Input(component_id='year-drop', component_property='value'))
def update_input_container3(selected_country, selected_year):
    if selected_year == 'All Years':
        df_filtered = df[df['country'] == selected_country] if selected_country != 'All Countries' else df
    else:
        df_filtered = df[(df['country'] == selected_country) & (df['year'] == selected_year)] if selected_country != 'All Countries' else df[df['year'] == selected_year]

    sides = df_filtered.groupby('region')[['deaths_a', 'deaths_b', 'deaths_civilians', 'deaths_unknown' ]].sum().reset_index()
    sides = sides.sort_values(by = 'region')

    

    bar5_fig = go.Figure()
    bar5_fig.add_trace(go.Bar(x=sides.region, y=sides.deaths_unknown, name='Unknown Deaths', text=sides['deaths_unknown'], textposition='outside'))
    bar5_fig.add_trace(go.Bar(x=sides.region, y=sides.deaths_a, name='Side A Deaths', text=sides['deaths_a'], textposition='outside'))
    bar5_fig.add_trace(go.Bar(x=sides.region, y=sides.deaths_b, name='Side B Deaths', text=sides['deaths_b'], textposition='outside'))
    bar5_fig.add_trace(go.Bar(x=sides.region, y=sides.deaths_civilians, name='Civilians Deaths', text=sides['deaths_civilians'], textposition='outside'))
    bar5_fig.update_layout(title='Count of Deaths per region for ' + selected_country + ' in ' + str(selected_year), xaxis_title='Region', yaxis_title='Total Deaths')
    R_chart5 = dcc.Graph(figure=bar5_fig)
    return [html.Div(className='chart-item', children=[R_chart5], style={'display': 'flex'})]
#;---------------
@app.callback(
    Output(component_id='output-container6', component_property='children'),
    [
        Input(component_id='country-drop', component_property='value'),
        Input(component_id='year-drop', component_property='value'),
        Input(component_id='deaths-type-radio', component_property='value')
    ]
)
def update_input_container6(selected_country, selected_year, selected_button):
    if selected_country == 'All Countries':
        if selected_year == 'All Years':
            df_filtered = df
        else:
            df_filtered = df[df['year'] == selected_year]
    else:
        if selected_year == 'All Years':
            df_filtered = df[df['country'] == selected_country]
        else:
            df_filtered = df[(df['country'] == selected_country) & (df['year'] == selected_year)]

    if selected_button == 'All Sides':
        sides = df_filtered.groupby(['country', 'ISO_Code'])['deaths_total'].sum().reset_index()
        z_values = sides['deaths_total']
    else:
        sides = df_filtered.groupby(['country', 'ISO_Code'])[selected_button].sum().reset_index()
        z_values = sides[selected_button]

    map_fig = go.Figure(data=go.Choropleth(
        locations=sides['ISO_Code'],
        z=z_values,
        text=sides['country'],
        colorscale='Blues',
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title='Value',
    ))

    R_chart6 = dcc.Graph(figure=map_fig)
    return [html.Div(className='chart-item', children=[R_chart6], style={'display': 'flex'})]
# Run the Dash app
if __name__ == "__main__":
	app.run_server(debug=False)
