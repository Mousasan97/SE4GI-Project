#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 16:33:34 2021

@author: alessandroaustoni
"""

from psycopg2 import (connect)
from werkzeug.security import  generate_password_hash

cleanup = (
        'DROP TABLE IF EXISTS jam_user CASCADE',
        'DROP TABLE IF EXISTS post'
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
        """,

        """ 
        CREATE TABLE post (
                post_id SERIAL PRIMARY KEY,
                author_id INTEGER NOT NULL,
                created TIMESTAMP DEFAULT NOW(),
                title VARCHAR(350) NOT NULL,
                body VARCHAR(500) NOT NULL,
                FOREIGN KEY (author_id)
                    REFERENCES jam_user (user_id)
        )
        """
#
#        """ 
#        CREATE TABLE requests_distresess (
#                request_id SERIAL PRIMARY KEY,
#                time TIME,
#                date DATE NOT NULL,
#                material VARCHAR(500) NOT NULL,
#                kind_distress VARCHAR(500) NOT NULL,
#                size VARCHAR(500) NOT NULL,
#                risk VARCHAR(500) NOT NULL,
#                latitude VARCHAR(500) NOT NULL,
#                longitude VARCHAR(500) NOT NULL,
#                FOREIGN KEY (user_mail_req)
#                    REFERENCES jam_user (user_mail)
#        )
#        """        
        )

sqlCommands = (
        'INSERT INTO jam_user (user_name, user_password, user_mail, admin) VALUES (%s, %s, %s, %s) RETURNING user_id',
        'INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)'
        )       

conn = connect("host='localhost' port='5433' dbname='postgres' user='postgres' password='admin'")
cur = conn.cursor()

for command in cleanup :
    cur.execute(command)
    
for command in commands :
    cur.execute(command)
    print('execute command')
    
cur.execute(sqlCommands[0], ('Giuseppe', generate_password_hash('3ety3e7'), 'giuseppe@aaa.com','0')) #admin=0 -> normal user | admin=1 -> specialized user | admin=2 -> Super User
pw='Geoinfo2021'
admin_pass=generate_password_hash(pw)
cur.execute(sqlCommands[0], ('JAM', admin_pass, 'mrnm.jam.team@gmail.com','2')) 
userId = cur.fetchone()[0]

cur.execute(sqlCommands[1], ('My First Post', 'This is the post body', userId))
cur.execute('SELECT * FROM post')
print(cur.fetchall())

cur.close()

conn.commit()
conn.close()
