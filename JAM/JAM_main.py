#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 23:45:58 2021

@author: alessandroaustoni
"""

from flask import (
    Flask, render_template, request, redirect, flash, url_for, session, g
)

from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.exceptions import abort

from psycopg2 import (
        connect
)

import json
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import requests


#<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

# Create the application instance
app = Flask(__name__, template_folder="templates")
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def get_dbConn():
    if 'dbConn' not in g:
        myFile = open('dbConfig.txt')
        connStr = myFile.readline()
        g.dbConn = connect(connStr)
    
    return g.dbConn

def close_dbConn():
    if 'dbConn' in g:
        g.dbComm.close()
        g.pop('dbConn')


@app.route('/map')
def map_():
    
    response = requests.get('https://five.epicollect.net/api/export/entries/MRNM?per_page=100')
    raw_data = response.text
    data = json.loads(raw_data)
    data_df = pd.json_normalize(data['data']['entries'])
    data_df['lat'] = pd.to_numeric(data_df['4_Specify_the_positi.longitude'], errors='coerce')
    data_df['lon'] =  pd.to_numeric(data_df['4_Specify_the_positi.latitude'], errors='coerce')
    data_geodf = gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df['lon'], data_df['lat']))
    m = folium.Map(location=[45.46, 9.19], zoom_start=13, tiles='CartoDB positron')
    marker_cluster = MarkerCluster().add_to(m)
    for indice, row in data_geodf.iterrows():
        folium.Marker(
            location=[row["lon"], row["lat"]],
            popup=row['7_Classify_the_distr'],
            icon=folium.map.Icon(color='red')
        ).add_to(marker_cluster)
    m.save('templates/map_outp.html')

    return render_template('map_fol.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mail = request.form['mail']
        type_ = request.form['type_']
        
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        elif not mail:
            error = 'Mail is required.'

        elif not type_:
            error = 'Kind of user is required.'
            
        else :
            conn = get_dbConn()
            cur = conn.cursor()
            cur.execute(
            'SELECT user_id FROM blog_user WHERE user_name = %s', (username,))
            if cur.fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
                cur.close()

        if error is None:
            conn = get_dbConn()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO blog_user (user_name, user_password, user_mail, user_type) VALUES (%s, %s, %s, %s)',
                (username, generate_password_hash(password), mail, type_,)
            )
            cur.close()
            conn.commit()
            return redirect(url_for('login'))

        flash(error)

    return render_template('auth/register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_dbConn()
        cur = conn.cursor()
        error = None
        cur.execute(
            'SELECT * FROM blog_user WHERE user_name = %s', (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.commit()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn = get_dbConn()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM blog_user WHERE user_id = %s', (user_id,)
        )
        g.user = cur.fetchone()
        cur.close()
        conn.commit()
    if g.user is None:
        return False
    else: 
        return True


# Create a URL route in our application for "/"
@app.route('/')
@app.route('/index')
def index():
    conn = get_dbConn()
    cur = conn.cursor()
    cur.execute(
            """SELECT blog_user.user_name, post.post_id, post.created, post.title, post.body 
               FROM blog_user, post WHERE  
                    blog_user.user_id = post.author_id"""
                    )
    posts = cur.fetchall()
    cur.close()
    conn.commit()
    load_logged_in_user()

    return render_template('blog/index.html', posts=posts)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if load_logged_in_user():
        if request.method == 'POST' :
            title = request.form['title']
            body = request.form['body']
            error = None
            
            if not title :
                error = 'Title is required!'
            if error is not None :
                flash(error)
                return redirect(url_for('index'))
            else : 
                conn = get_dbConn()
                cur = conn.cursor()
                cur.execute('INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)', 
                            (title, body, g.user[0])
                            )
                cur.close()
                conn.commit()
                return redirect(url_for('index'))
        else :
            return render_template('blog/create.html')
    else :
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('login'))
   
def get_post(id):
    conn = get_dbConn()
    cur = conn.cursor()
    cur.execute(
        """SELECT *
           FROM post
           WHERE post.post_id = %s""",
        (id,)
    )
    post = cur.fetchone()
    cur.close()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if post[1] != g.user[0]:
        abort(403)

    return post

@app.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    if load_logged_in_user():
        post = get_post(id)
        if request.method == 'POST' :
            title = request.form['title']
            body = request.form['body']
            error = None
            
            if not title :
                error = 'Title is required!'
            if error is not None :
                flash(error)
                return redirect(url_for('index'))
            else : 
                conn = get_dbConn()
                cur = conn.cursor()
                cur.execute('UPDATE post SET title = %s, body = %s'
                               'WHERE post_id = %s', 
                               (title, body, id)
                               )
                cur.close()
                conn.commit()
                return redirect(url_for('index'))
        else :
            return render_template('blog/update.html', post=post)
    else :
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('login'))

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    conn = get_dbConn()                
    cur = conn.cursor()
    cur.execute('DELETE FROM post WHERE post_id = %s', (id,))
    conn.commit()
    return redirect(url_for('index'))                               

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)
print('doneeee');    
    