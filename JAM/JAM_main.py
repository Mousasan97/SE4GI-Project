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
from sqlalchemy import create_engine
import json
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import requests
from string import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from make_graphs import dash_

#<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

# Create the application instance
app = Flask(__name__, template_folder="templates")
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

engine = create_engine('postgresql://JAM:SWfire07@localhost:5432/JAM_db')   

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def get_dbConn():
    if 'dbConn' not in g:
        myFile = open('dbConfig.txt')
        connStr = myFile.readline()
        g.dbConn = connect(connStr)
    
    return g.dbConn

def update_req_ep5():
    
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

    # conn = connect("host='localhost' port='5433' dbname='postgres' user='postgres' password='admin'")
    
    # cur = conn.cursor()
    
    # distress_update = ("ALTER TABLE ep5 ADD status_request varchar(255) DEFAULT 'ON_GOING'")
    
    # cur.execute(distress_update)

update_req_ep5()


def close_dbConn():
    if 'dbConn' in g:
        g.dbComm.close()
        g.pop('dbConn')

@app.route('/user_requests', methods=('GET', 'POST'))        
def requests_user():
    loading=load_admin() #now we are passing a list
    if loading[0]==0:
        flash('you should login for seeing user requests')
        return redirect(url_for('login'))
    else:
        user_mail=loading[0] #Mail of user
        conn = get_dbConn()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM ep5 WHERE "3_Enter_Your_Email" = %s', (user_mail,)
        )
        
        df_requests = cur.fetchall()
        
        cur.close()
        conn.commit()
        return render_template('distresess_user.html', ep5=df_requests)

##TO MERGE INTO A UNIQUE FUNCTION WITH THE PREVIOUS ONE AND IMPLEMENT
# @app.route('/modify_requests', methods=('GET', 'POST'))        
# def change_status():

#     update_req_ep5()
    
#     conn = get_dbConn()
#     cur = conn.cursor()
       
#     cur.execute('SELECT * FROM ep5')
    
#     df_requests = cur.fetchall()
 
#     dataframe_requests=pd.DataFrame(df_requests)
    
#     if request.method == 'POST':

#           for row in range(len(dataframe_requests)):
             
#              if request.form['submit_button'] == row[0]:
    
#                      distress_update = ("UPDATE TABLE ep5 SET status_request='IN_CHARGE' WHERE ec5_uuid == %s", (row[0],))
    
#                      cur.execute(distress_update)
    
#     cur.close()
#     conn.commit()
    
#     return render_template('userrequests/index.html', ep5=df_requests)

@app.route('/admin-request', methods=('GET', 'POST'))
def registeradmin():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        role = request.form['role']
        department = request.form['department']
        phone = request.form['phone']
        
        error = None

        if not name:
            error = 'name is required.'
        elif not surname:
            error = 'surname is required.'

        elif not role:
            error = 'role is required.'

        elif not department:
            error = 'Work department is required.'
            
        elif not phone:
            error = 'phone number is required to be contacted by the admin.'    
            
        else :
            #insert here the code for sending the email
            email_template=read_template('message.txt')
            # set up the SMTP server
            s = smtplib.SMTP(host='smtp.gmail.com', port=587)
            s.starttls()
            s.login('mrnm.requesthandler@gmail.com', 'SWfire07')
            msg = MIMEMultipart()       # create a message
            # add in the actual information to the message template
            message = email_template.substitute(U_NAME=name,U_SURNAME=surname,U_ROLE=role,U_DEPARTMENT=department,U_PHONE=phone)
            msg['From']='mrnm.requesthandler@gmail.com'
            msg['To']='mrnm.jam.team@gmail.com'
            msg['Subject']="ADMIN SUBMISSION REQUEST"
            # add in the message body
            msg.attach(MIMEText(message, 'plain'))
            # send the message via the server set up earlier.
            s.send_message(msg)
    
            del msg
            return redirect(url_for('success'))

        flash(error)

    return render_template('auth/register-admin.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/access-denied')
def access_denied():
    return render_template('access_denied.html')

@app.route('/dash')
def dash_make():
    [email,user_type]=load_admin()
    if user_type==0 or user_type==None:
        return redirect(url_for('access_denied'))
    #Invoke the function that is in the script "make_graphs.py" which create all the HTML files of the graphs for the webapp
    else:
        dash_()
   
    #Then, Jinja renders the html template with all the graphs.  
    return render_template('dash_templ.html')

@app.route('/map')
def map_():
    
    data_geodf=update_req_ep5()
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

@app.route('/admin-register', methods=('GET', 'POST'))
def admin_register():

    loading=load_admin()
    user_type=loading[1]
    if user_type==0 or user_type==None or user_type==1:

        return redirect(url_for('access_denied'))
    else :
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            mail = request.form['mail']
            type_ = 1
            
            error = None
    
            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
    
            elif not mail:
                error = 'Mail is required.'
                
            else :
                conn = get_dbConn()
                cur = conn.cursor()
                cur.execute(
                'SELECT user_id FROM jam_user WHERE user_name = %s', (username,))
                if cur.fetchone() is not None:
                    error = 'User {} is already registered.'.format(username)
                    cur.close()
    
            if error is None:
                conn = get_dbConn()
                cur = conn.cursor()
                cur.execute(
                    'INSERT INTO jam_user (user_name, user_password, user_mail, admin) VALUES (%s, %s, %s, %s)',
                    (username, generate_password_hash(password), mail, type_,)
                )
                cur.close()
                conn.commit()
                return redirect(url_for('login'))
    
            flash(error)
    
        return render_template('auth/register.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mail = request.form['mail']
        type_ = 0
        
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        elif not mail:
            error = 'Mail is required.'
            
        else :
            conn = get_dbConn()
            cur = conn.cursor()
            cur.execute(
            'SELECT user_id FROM jam_user WHERE user_name = %s', (username,))
            if cur.fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
                cur.close()

        if error is None:
            conn = get_dbConn()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO jam_user (user_name, user_password, user_mail, admin) VALUES (%s, %s, %s, %s)',
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
            'SELECT * FROM jam_user WHERE user_name = %s', (username,)
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
            'SELECT * FROM jam_user WHERE user_id = %s', (user_id,)
        )
        g.user = cur.fetchone()
        cur.close()
        conn.commit()
    if g.user is None:
        return False
    else: 
        return True

def load_admin():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        admin=0
        mail=0
    else:
        conn = get_dbConn()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM jam_user WHERE user_id = %s', (user_id,)
        )
        g.user = cur.fetchone()
        mail=g.user[3]
        admin=g.user[4]
        cur.close()
        conn.commit()
    return [mail, admin]


# Create a URL route in our application for "/"
@app.route('/')
@app.route('/index')
def index():
    conn = get_dbConn()
    cur = conn.cursor()
    cur.execute(
            """SELECT jam_user.user_name, post.post_id, post.created, post.title, post.body 
               FROM jam_user, post WHERE  
                    jam_user.user_id = post.author_id"""
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
    app.run(debug=False)
print('doneeee');    
    