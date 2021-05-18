#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 16:33:34 2021

@author: alessandroaustoni
"""

from psycopg2 import connect

cleanup = (
        'DROP TABLE IF EXISTS jam_table CASCADE'
        )

commands = (
    'CREATE TABLE jam_table (user_id SERIAL PRIMARY KEY,user_name VARCHAR(255),user_password VARCHAR(255))'
        )

sqlCommands = (
        'INSERT INTO jam_table (user_name, user_password) VALUES (%s, %s) RETURNING user_id'
        )

conn = connect("dbname=JAM_db user=JAM password=SWfire07")
cur = conn.cursor()
cur.execute(cleanup)
cur.execute(commands)
print('execute command')
cur.execute(sqlCommands, ('Giuseppe', '3ety3e7'))
userId = cur.fetchone()[0]
cur.close()
conn.commit() 
conn.close()