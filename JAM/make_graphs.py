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
    
    req_user=data_df.groupby(['3_Enter_Your_Email']).count()
    req_user=req_user.iloc[:,1]
    req_user=pd.DataFrame(req_user)
    req_user["Quantity"]=req_user.iloc[:,-1]
    req_user["User"]=req_user.index
    
    day_req=data_df.groupby(['2_Enter_Date']).count()
    day_req=day_req.iloc[:,1]
    day_req=pd.DataFrame(day_req)
    day_req["Quantity"]=day_req.iloc[:,-1]
    day_req["Day"]=day_req.index
    
    a=list(Size_distres['Category'])
    b=list(Size_distres['Quantity'])
    
    c=list(Material['Category'])
    d=list(Material['Quantity'])
    
    e=list(Kind_of_distres['Category'])
    f=list(Kind_of_distres['Quantity'])
    
    g=list(Risk_level['Category'])
    h=list(Risk_level['Quantity'])

    i=list(req_user['User'])
    j=list(req_user['Quantity'])
    
    k=list(day_req['Day'])
    l=list(day_req['Quantity'])
    
    data_geodf["size_chart"]=10
    
    fig = px.scatter_mapbox(data_geodf, lat="lon", 
                            lon="lat", 
                            hover_name="7_Classify_the_distr", 
                            hover_data=['7_Classify_the_distr'],
                            size="size_chart",
                            color_discrete_sequence=["Gold"], 
                            zoom=12,
                            opacity=0.6,
                            height=400)
    
    
    fig.update_geos(fitbounds="locations")
    
    fig.update_layout(mapbox_style="open-street-map")
    
    fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    
    fig.update_layout(font_family="Roboto",font_color="white")
    
    fig.update_layout(template="plotly_dark")    
    
    fig.write_html("templates/map_analytics.html")
    
    # Use the hovertext kw argument for hover text
    fig2 = go.Figure(data=[go.Scatter(x=a, y=b,
                hovertext=a)])
    # Customize aspect
    fig2.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig2.update_layout(title_text='Size of distreses')

    fig2.update_layout(font_family="Roboto",font_color="white")

    fig2.update_layout(template="plotly_dark")    

    fig2.write_html("templates/bar_size.html")

    fig3 = go.Figure(data=[go.Scatter(x=c, y=d,hovertext=c)])
    # Customize aspect
    fig3.update_traces(marker_color='rgb(220,20,60)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig3.update_layout(title_text='Material')

    fig3.update_layout(font_family="Roboto",font_color="white")

    fig3.update_layout(template="plotly_dark")    

    fig3.write_html("templates/bar_material.html")

    fig4 = go.Figure(data=[go.Scatter(x=e, y=f,
                hovertext=e)])
    # Customize aspect
    fig4.update_traces(marker_color='rgb(255,165,0)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig4.update_layout(title_text='Kind of Distreses')

    fig4.update_layout(font_family="Roboto",font_color="white")

    fig4.update_layout(template="plotly_dark")    

    fig4.write_html("templates/bar_kind_of_distr.html")

    fig5 = go.Figure(data=[go.Scatter(x=g, y=h,
                hovertext=g)])
    # Customize aspect
    fig5.update_traces(marker_color='rgb(0,100,0)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig5.update_layout(title_text='Level of Risk')

    fig5.update_layout(font_family="Roboto",font_color="white")

    fig5.update_layout(template="plotly_dark")    

    fig5.write_html("templates/bar_risk.html")

    fig6 = go.Figure(data=[go.Bar(x=i, y=j,
                hovertext=i)])
    # Customize aspect
    fig6.update_traces(marker_color='rgb(100,100,0)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig6.update_layout(title_text='Requests of maintenance per user')

    fig6.update_layout(font_family="Roboto",font_color="white")

    fig6.update_xaxes(categoryorder='total ascending')

    fig6.update_layout(template="plotly_dark")    

    fig6.write_html("templates/user_req_plot.html")
    
    
    fig7 = go.Figure(data=[go.Bar(x=k, y=l,
                hovertext=k)])
    # Customize aspect
    fig7.update_traces(marker_color='rgb(100,100,0)', marker_line_color='rgb(128,128,128)',
                      marker_line_width=1.5, opacity=0.6)
    fig7.update_layout(title_text='Requests of maintenance per day')

    fig7.update_layout(font_family="Roboto",font_color="white")

    fig7.update_layout(template="plotly_dark")    

    fig7.write_html("templates/req_day_plot.html")    
    
    
    