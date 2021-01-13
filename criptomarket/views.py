from criptomarket import app
from criptomarket.forms import *
from flask import render_template, request, url_for, redirect, flash, Response
import sqlite3
from datetime import date
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# Atajo conexión base de datos y API
DBFILE = app.config['DBFILE']
API_KEY = app.config['API_KEY']


# Función de la query a la BD
def consulta(query, params=()):
    conn = sqlite3.connect(DBFILE)
    c = conn.cursor()

    c.execute(query, params)
    conn.commit()

    filas = c.fetchall()

    conn.close()

# Renderizado home
@app.route('/')
def index():
    return render_template('index.html')

# Renderizado registro
@app.route('/compra', methods=['GET', 'POST'])
def registre():

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'1',
    'convert':'EUR',
    
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as errores:
        print(errores)
    

    form = RegisterForm(request.form)
    
    if request.method == 'POST':
        print("El methodo ha sido post!")
        if form.validate():
            print("Se ha validado!")
            consulta('INSERT INTO users (password, email, fecha_alta) VALUES (?, ? ,? );', 
                    (
                        form.password_registre.data,
                        form.email_registre.data,
                        date.today(),
                    )
            )

            return redirect(url_for('compra'))
        else:
            return render_template("compra.html", form=form)
            
    return render_template("compra.html", form=form)

