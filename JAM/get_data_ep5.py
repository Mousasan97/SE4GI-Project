# -*- coding: utf-8 -*-
"""
Created on Sat May 29 01:11:51 2021

@author: Juanfra
"""
import pandas as pd
import geopandas as gpd
import requests
import json
from sqlalchemy import create_engine

def update_req_ep5():
    
    engine = create_engine('postgresql://JAM:SWfire07@localhost:5432/JAM_db')
    #engine = create_engine('postgresql://postgres:admin@localhost:5433/postgres')
    response = requests.get('https://five.epicollect.net/api/export/entries/MRNM?per_page=100')
    raw_data = response.text
    data = json.loads(raw_data)
    data_df = pd.json_normalize(data['data']['entries'])
    data_df['lat'] = pd.to_numeric(data_df['4_Specify_the_positi.longitude'], errors='coerce')
    data_df['lon'] =  pd.to_numeric(data_df['4_Specify_the_positi.latitude'], errors='coerce')
    data_df["status_request"]="ON_GOING"
    # data_df=data_df.rename(columns={'3_Enter_Your_Email':'user_mail'})
    data_geodf = gpd.GeoDataFrame(data_df,geometry=gpd.points_from_xy(data_df['lon'], data_df['lat']))
    data_geodf.to_postgis('ep5', engine, if_exists='replace')
    
    return data_geodf