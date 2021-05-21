# -*- coding: utf-8 -*-

import json
import pandas as pd
import geopandas as gpd
import requests
import plotly.express as px
import plotly.graph_objects as go

def dash_():

    response = requests.get('https://five.epicollect.net/api/export/entries/MRNM?per_page=100')
    raw_data = response.text
    data = json.loads(raw_data)
    data_df = pd.json_normalize(data['data']['entries'])
    data_df['lat'] = pd.to_numeric(data_df['4_Specify_the_positi.longitude'], errors='coerce')
    data_df['lon'] =  pd.to_numeric(data_df['4_Specify_the_positi.latitude'], errors='coerce')
    data_geodf = gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df['lon'], data_df['lat']))

    Size_distres=data_df.groupby(['8_Set_the_size_of_th']).count()
    Size_distres=Size_distres.iloc[:,1]
    Size_distres=pd.DataFrame(Size_distres)
    Size_distres["Quantity"]=Size_distres.iloc[:,-1]
    Size_distres["Category"]=Size_distres.index

    Material=data_df.groupby(['6_Specify_the_type_o']).count()
    Material=Material.iloc[:,1]
    Material=pd.DataFrame(Material)
    Material["Quantity"]=Material.iloc[:,-1]
    Material["Category"]=Material.index
    
    Kind_of_distres=data_df.groupby(['7_Classify_the_distr']).count()
    Kind_of_distres=Kind_of_distres.iloc[:,1]
    Kind_of_distres=pd.DataFrame(Kind_of_distres)
    Kind_of_distres["Quantity"]=Kind_of_distres.iloc[:,-1]
    Kind_of_distres["Category"]=Kind_of_distres.index
    
    Risk_level=data_df.groupby(['9_Determine_the_leve'],  axis=0).count()
    Risk_level=Risk_level.iloc[:,1]
    Risk_level=pd.DataFrame(Risk_level)
    Risk_level["Quantity"]=Risk_level.iloc[:,-1]
    Risk_level["Category"]=Risk_level.index
    
    a=list(Size_distres['Category'])
    b=list(Size_distres['Quantity'])
    
    c=list(Material['Category'])
    d=list(Material['Quantity'])
    
    e=list(Kind_of_distres['Category'])
    f=list(Kind_of_distres['Quantity'])
    
    g=list(Risk_level['Category'])
    h=list(Risk_level['Quantity'])
    
    
    fig = px.scatter_mapbox(data_geodf, lat="lon", lon="lat", hover_name="7_Classify_the_distr", hover_data=['7_Classify_the_distr'],
                            color_discrete_sequence=["fuchsia"], zoom=15, height=300)
    
    fig.update_geos(fitbounds="locations")
    
    fig.update_layout(mapbox_style="open-street-map")
    
    fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    
    fig.update_layout(font_family="Roboto",font_color="blue")
    
    fig.write_html("templates/map_analytics.html")
    
    # Use the hovertext kw argument for hover text
    fig2 = go.Figure(data=[go.Bar(x=a, y=b,
                hovertext=a)])
    # Customize aspect
    fig2.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig2.update_layout(title_text='Size of distreses')

    fig2.update_layout(font_family="Roboto",font_color="blue")

    fig2.write_html("templates/bar_size.html")

    fig3 = go.Figure(data=[go.Bar(x=c, y=d,
                hovertext=c)])
    # Customize aspect
    fig3.update_traces(marker_color='rgb(220,20,60)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig3.update_layout(title_text='Material')

    fig3.update_layout(font_family="Roboto",font_color="blue")

    fig3.write_html("templates/bar_material.html")

    fig4 = go.Figure(data=[go.Bar(x=e, y=f,
                hovertext=e)])
    # Customize aspect
    fig4.update_traces(marker_color='rgb(255,165,0)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig4.update_layout(title_text='Kind of Distreses')

    fig4.update_layout(font_family="Roboto",font_color="blue")

    fig4.write_html("templates/bar_kind_of_distr.html")

    fig5 = go.Figure(data=[go.Bar(x=g, y=h,
                hovertext=g)])
    # Customize aspect
    fig5.update_traces(marker_color='rgb(0,100,0)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig5.update_layout(title_text='Level of Risk')

    fig5.update_layout(font_family="Roboto",font_color="blue")

    fig5.write_html("templates/bar_risk.html")



