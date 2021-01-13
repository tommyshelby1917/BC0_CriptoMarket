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

# Conexion con la API y las 10 monedas más valuosas
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
'start':'1',
'limit':'1000',
'convert':'EUR',
'sort':'price',
}
headers = {
'Accepts': 'application/json',
'X-CMC_PRO_API_KEY': API_KEY,
}

session = Session()
session.headers.update(headers)

# Recolecta datos JSON y Control errores
try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    
except (ConnectionError, Timeout, TooManyRedirects) as errores:
    print(errores)

# Receta creacion diccionario de las 10 monedas más valiosa
unidad_monedas_top10 = []
precio_monedas_top10 = []
for i in range(10):
    precio_monedas_top10.append(round(data['data'][i]['quote']['EUR']['price'], 2))
    unidad_monedas_top10.append(data['data'][i]['symbol'])

dict_monedas_top10 = dict(zip(unidad_monedas_top10,precio_monedas_top10))
for i in dict_monedas_top10:
    print(f"{i}: {dict_monedas_top10[i]}")


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
    return render_template('index.html', dict_monedas_top10=dict_monedas_top10)

# Renderizado registro
@app.route('/purchase', methods=['GET', 'POST'])
def registre():
    
    # Formulario compra
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

            return redirect(url_for('purchase'))
        else:
            return render_template("purchase.html", form=form)
            
    return render_template("purchase.html", form=form)

