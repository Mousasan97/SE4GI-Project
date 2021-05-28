# -*- coding: utf-8 -*-
"""
Created on Sat May 29 01:09:04 2021

@author: Juanfra
"""
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from get_data_ep5 import update_req_ep5


def map_():
    
    data_geodf=update_req_ep5()
    
    m = folium.Map(location=[45.46, 9.19], zoom_start=13)
    
    marker_cluster = MarkerCluster().add_to(m)
    
    for indice, row in data_geodf.iterrows():
        folium.Marker(
            location=[row["lon"], row["lat"]],
            popup=row['7_Classify_the_distr'],
            icon=folium.map.Icon(color='red')
        ).add_to(marker_cluster)
    
    tiles = ['stamenwatercolor', 'cartodbpositron', 'openstreetmap', 'stamenterrain']
    
    for tile in tiles:
        
        folium.TileLayer(tile).add_to(m)
    
    milano = gpd.read_file("ace_maggio_2011.geojson")
    csv_milano=pd.read_csv(r"ace_maggio_2011_4326.csv", sep=";")
    
    folium.Choropleth(geo_data=milano,
                        name="choropleth",
                        data=csv_milano,
                        columns=["ACE","SUM_POP_20"],
                        key_on="feature.properties.ACE",
                        fill_color="YlGnBu",
                        fill_opacity=0.7,
                        line_opacity=0.2,
                        legend_name="POPULATION",
                            ).add_to(m)
    
    folium.LayerControl().add_to(m)

    m.save('templates/map_outp.html')