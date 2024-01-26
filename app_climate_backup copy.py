#import libraries
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
from sqlalchemy import text

#env
username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')

#get the data
df_climate_final = pd.read_csv("climate_final.csv")
df_monthly_final = pd.read_csv("df_monthly_final.csv")
df_temp = pd.read_csv("df_temp.csv")
df_monthly_avg = pd.read_csv("df_monthly_avg.csv")
monthly_final_download = df_monthly_final.to_csv(index = False, encoding = "utf-8")

#set up the color code
#BAR CHART COLOR CHOICES

color_palette = {
                'Berlin': '#6495ed', #blue
                'Madrid': '#ffb347', #orange
                'Paris': '#e6a8d7', #purple
                'Tel Aviv-Yafo': '#93c572'} #green

#TEXT COLOR CHOICES
text = "#808080"
legend = "#191970"
#background colors for each graph 
plot_bgcolor="#e3dac9" #tan colors
paper_bgcolor="#e3dac9"
font_color="#191970"
#titles 
title_font = "#191970"
color_berlin = '#6495ed' #blue
color_madrid = '#ffb347' #orange 
color_paris = '#e6a8d7' #purple
color_tel_aviv = '#93c572'#green

#set up the tables 
#graph 1) world view
df_climate_final["date"].min(), df_climate_final["date"].max()

graph1= px.choropleth(df_climate_final[df_climate_final["date"]=="2023-02-14"], 
                      locations = "country", 
                      projection = "natural earth",
                      scope = "world",
                      color_continuous_scale=px.colors.sequential.Reds,
                      color = "avg_temp",
                      locationmode ='country names')

# Set the background color
bg_color = plot_bgcolor  # Replace with your desired color, e.g., '#f0f0f0'
graph1.update_layout(
    paper_bgcolor=bg_color,  # Background color for the whole figure
    plot_bgcolor="blue", # Background color for the plotting area only
    geo_bgcolor=bg_color
)
graph1 = dcc.Graph(figure=graph1)

#let's create a line chart with the focus on Berlin (average max and min temperature in the respective month

#set up the dataframe
df_temp_new = df_temp[["date", "maxtemp_c", "mintemp_c","city", "month", "month_num"]]

# Group the DataFrame by month and city and calculate the mean for maxtemp_c and mintemp_c
grouped = df_temp_new.groupby(['month', 'city'])[['maxtemp_c', 'mintemp_c']].mean().round(2).reset_index()

# Rename the columns to indicate average values
grouped.rename(columns={'maxtemp_c': 'avg_maxtemp_c', 'mintemp_c': 'avg_mintemp_c'}, inplace=True)

# Merge the grouped data back into the original DataFrame
df_line = df_temp_new.merge(grouped, on=['month', 'city'], how='left')
#plotting the graph
fig3 = px.line(df_line, x='month', y='avg_maxtemp_c', height=300, title="Average Maximum Temperature", markers=True, color = "city", color_discrete_map =color_palette,)
fig3 = fig3.update_layout(
    xaxis_title=dict(text="Month", font=dict(color=legend)),
    yaxis_title=dict(text="Average Temperature (°C)", font=dict(color=legend)),
    xaxis=dict(tickfont=dict(color=legend)),
    yaxis=dict(tickfont=dict(color=legend)),
    plot_bgcolor=plot_bgcolor,
    paper_bgcolor=paper_bgcolor,
    font_color=font_color,   
    )
graph3 = dcc.Graph(figure=fig3) #make it ready for the dash

#lets create a bar chart with all of them
    # df creation
df_temp_month = df_temp.groupby(['month', "city","month_num"])['avgtemp_c'].mean().round(2).reset_index()
df_temp_month.sort_values(by="month_num", ascending = True, inplace = True)

    #plotting the graph
fig2 = px.bar(df_temp_month,
             x = "month",
             y = 'avgtemp_c',
             color = "city",
             color_discrete_map =color_palette,
             barmode = "group",
             height = 300,
             title = "Average Temperature in 2023 - A Comparison between the four cities",
             )

# Customize the title, axis titles, and descriptions colors
fig2.update_layout(
    title=dict(text="Average Temperature in 2023 - A Comparison between the four cities", font=dict(color=title_font)),
    xaxis_title=dict(text="Month", font=dict(color=legend)),
    yaxis_title=dict(text="Average Temperature (°C)", font=dict(color=legend)),
    xaxis=dict(tickfont=dict(color=legend)),
    yaxis=dict(tickfont=dict(color=legend)),
    plot_bgcolor=plot_bgcolor,
    paper_bgcolor=paper_bgcolor,
    font_color=font_color,
)
graph2 = dcc.Graph(figure=fig2)
#lets add the df_monthly_avg to the dash: 
d_table1 = dash_table.DataTable(df_monthly_avg.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_monthly_avg.columns],
                               style_data={'color': "white",'backgroundColor': plot_bgcolor},
                               style_header={'backgroundColor': plot_bgcolor,
                                             'color': title_font,'fontWeight': 'bold', "textAlign":"center",'padding': 10})
#new line graph; average min 
#plotting the graph
fig4 = px.line(df_line, x='month', y='avg_mintemp_c', height=300, title="Average Minimum Temperature", markers=True, color = "city", color_discrete_map =color_palette)
fig4 = fig4.update_layout(
    xaxis_title=dict(text="Month", font=dict(color=legend)),
    yaxis_title=dict(text="Average Minimum Temperature (°C)", font=dict(color=legend)),
    xaxis=dict(tickfont=dict(color=legend)),
    yaxis=dict(tickfont=dict(color=legend)),
    plot_bgcolor=plot_bgcolor,
    paper_bgcolor=paper_bgcolor,
    font_color=font_color,   
    )
graph4 = dcc.Graph(figure=fig4) #make it ready for the dash

fig4.show()



#setting up the theme
app = dash.Dash(external_stylesheets=[dbc.themes.UNITED])
server = app.server

app = dash.Dash(external_stylesheets=[dbc.themes.UNITED])

dropdown1 = dcc.Dropdown(
    id='dropdown1',  # simple string ID
    options=[{'label': 'Berlin', 'value': 'Berlin'}, {'label': 'Paris', 'value': 'Paris'}, {'label': 'Madrid', 'value': 'Madrid'}, {'label': 'Tel Aviv-Yafo', 'value': 'Tel Aviv-Yafo'}],
    value='Berlin',  # default value
    clearable=False,
    style={'backgroundColor': 'plot_bgcolor', 'color': 'white'}
)


server = app.server

# Setting up the layout
app.layout = html.Div([
    html.Div([
        html.H1('My First Spicy Dash', style={'textAlign': 'center', 'color': title_font, 'fontSize': '50px', 'fontWeight': 'bold', "backgroundColor": plot_bgcolor, 'margin': '0', 'padding': 10}),
        html.H2('A Dashboard designed by Franziska Oschmann', style={'textAlign': 'center', 'color': title_font, 'fontSize': '30px', 'fontWeight': 'bold', "backgroundColor": plot_bgcolor, 'margin': '0', 'padding': 10}),
        html.H3('24 January 2024', style={'textAlign': 'center', 'color': title_font, 'fontSize': '20px', 'fontWeight': 'bold', "backgroundColor": plot_bgcolor, 'margin': '0', 'padding': 10}),
        html.H4("This Dashboard provides an overview about the weather in Paris, Berlin, Madrid and Tel Aviv: Enjoy exploring it",
                style={'textAlign': 'center','fontWeight': 'bold', "color":title_font, "backgroundColor": plot_bgcolor, 'margin': '0', 'padding': 10})
    ]),
    html.Div([
        html.H3("Here you can find the world view", style={'textAlign': 'center', 'color': title_font, 'fontSize': '30px', "backgroundColor": plot_bgcolor, 'margin': '0', 'padding': 10}),
        graph1,
        html.H3("This is a table showing you the average temperature in 2023 per month in the cities I lived in", style = {"color": title_font, 'fontSize':'10 px',"backgroundColor": plot_bgcolor, 'margin': '0', 'padding': 10}),
        d_table1,graph3, dropdown1, 
        graph2
    ])
]) 

@callback(
    Output(graph2, "figure"), 
    Input(dropdown1, "value"))

def update_bar_chart(country): 
    mask = df_temp_month["city"] == country
    fig =px.bar(df_temp_month[mask], 
             x='month', 
             y='avgtemp_c',  
             color="city",
             barmode='group',
             height=300, 
            color_discrete_map = color_palette)
    fig = fig.update_layout(
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
        font_color=font_color
    )
    return fig # whatever you are returning here is connected to the component property of
                       #the output which is figure
# Run the app
if __name__ == '__main__':
    app.run_server(host= "localhost", port = "8050", debug = True)