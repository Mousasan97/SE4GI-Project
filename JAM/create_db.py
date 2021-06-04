#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 16:33:34 2021

@author: alessandroaustoni
"""

from psycopg2 import (connect)
from werkzeug.security import  generate_password_hash

cleanup = (
        'DROP TABLE IF EXISTS jam_user CASCADE'
      
        )

commands = (
        """
        CREATE TABLE jam_user (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) UNIQUE NOT NULL,
            user_password VARCHAR(255) NOT NULL,
            user_mail VARCHAR(255) UNIQUE NOT NULL,
            admin INTEGER

        )
        """  
        )

sqlCommands = (
        'INSERT INTO jam_user (user_name, user_password, user_mail, admin) VALUES (%s, %s, %s, %s) RETURNING user_id'
        )       

conn = connect("host='localhost' port='5432' dbname='postgres' user='postgres' password='Alhamdulilah1_'")

# conn = connect("host='localhost' port='5432' dbname='JAM_db' user='JAM' password='SWfire07'")
#conn = connect("host='localhost' port='5433' dbname='postgres' user='postgres' password='admin'")
cur = conn.cursor()


cur.execute(cleanup)
    

cur.execute(commands)
print('execute command')
    
cur.execute(sqlCommands, ('Giuseppe', generate_password_hash('3ety3e7'), 'giuseppe@aaa.com','0')) #admin=0 -> normal user | admin=1 -> specialized user | admin=2 -> Super User
pw='Geoinfo2021'
admin_pass=generate_password_hash(pw)
cur.execute(sqlCommands, ('JAM', admin_pass, 'mrnm.jam.team@gmail.com','2')) 
pw2='special'
special_pass=generate_password_hash(pw2)
cur.execute(sqlCommands, ('Specialized_user', admin_pass, 'special@gmail.com','1')) 
userId = cur.fetchone()[0]


print(cur.fetchall())

cur.close()

conn.commit()
conn.close()
