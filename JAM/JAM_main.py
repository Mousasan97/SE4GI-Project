#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 23:45:58 2021

@author: alessandroaustoni
"""


from flask import (Flask, render_template)

app = Flask(__name__, template_folder="templates")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/viewMap')
def viewMap():
    return 'Hi I am the map :)'

@app.route('/login')
def login():
    return 'Hi I am the login :)'
    
if __name__ == '__main__':
    app.run(debug=True)