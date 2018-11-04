#Imports
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd


#Read in Master Dataset, extract subjects
df_master = pd.read_csv("data/HNP_StatsData.csv")
subjects = ["Unemployment, total (% of total labor force)", 
            "Public spending on education, total (% of GDP)", 
            "GNI per capita, Atlas method (current US$)"]
df_target = df_master.loc[df_master['Indicator Name'].isin(subjects)]

#Clean df for further analysis
df_target.drop('Country Code', axis=1, inplace=True)
df_target.drop('Indicator Code', axis=1, inplace=True)
df = (df_target.pivot(index='Country Name',columns='Indicator Name')
   .stack(0)
   .rename_axis(['Country','Year'])
   .reset_index())

#Read in all Latin American Countries
df_latin = pd.read_csv("data/latin_america.csv")
countries_all = df_latin["Country"]


#Initiate App
app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

#Create Layout
app.layout = html.Div([
    
    html.Div([ 
        html.H3(children='Data Explorer: Latin America'),
        dcc.Dropdown(
            id='x-axis-name',
            options=[
                {'label': 'GNI per Capita (USD)', 'value': subjects[2]},
                {'label': 'Public spending on education (% of GDP)', 'value': subjects[1]}
            ],
            value=subjects[2]
        ),
        dcc.Dropdown(
                id='countries',
            options=[{'label': c, 'value': c} for c in countries_all],
            value=[c for c in countries_all[:12]],
            multi=True
        )
    ],
    style={'min-width': '500px', 'width': '48%', 'margin-bottom': '40px', 'margin-left':'10px'}),
    
    html.Div([
        dcc.Graph(id='indicator-graphic'),
    ], 
    style={'min-width': '800px', 'width': '55%', 'margin-top': '30px', 'margin-left':'10px'}),
   
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=1990,
            max=2016,
            marks={i: '{}'.format(i) for i in range(1992, 2016, 4)},
            value=1992,
        )
   ],
   style={'width': '48%', 'margin-top': '30px', 'margin-left':'10px'})
])


#Callback Logic
@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('x-axis-name', 'value'),
     dash.dependencies.Input('countries', 'value'),
     dash.dependencies.Input('year-slider', 'value')])
        
def update_graph(xaxis, countries, year):
    df_cut = df[df["Country"].isin(countries)]
    years = [str(year),str(year+1),str(year+2),str(year+3)]
    if xaxis == subjects[1]: 
        df_cut.drop([subjects[2]], axis=1, inplace=True)
        xrange = [0.01, 14.9]
    elif xaxis == subjects[2]: 
        df_cut.drop([subjects[1]], axis=1, inplace=True)
        xrange = [0.01, 24500]
    df_cut = df[df["Year"].isin(years)]
    df_cut = df_cut.dropna(axis=0, how="any")
    
    return {
        'data': [
            go.Scatter(
                x = df_cut[df_cut["Country"] == c][xaxis],
                y = df_cut[df_cut["Country"] == c][subjects[0]],
                text = "Jahr: "+df_cut[df_cut['Country'] == c]["Year"],
                mode = 'markers',
                opacity = 0.7,
                marker= {
                    'size': 12,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=c
            ) for c in countries
        ],
        'layout': go.Layout(
            xaxis = dict(range=xrange, title = xaxis),
            yaxis = dict(range=[0.01, 21], title = "Unemployment in %"),
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0.85, 'y': 0.95},
            hovermode='closest'
        )
    }  

#Main
if __name__ == '__main__':
    app.run_server()