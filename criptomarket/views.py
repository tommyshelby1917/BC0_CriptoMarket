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

# Conexion con la API y parámetros
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
'convert':'EUR',
'symbol':'ETH,LTC,BNB,EOS,XLM,TRX,BTC,XRP,BCH,USDT,BSV,ADA'
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

# Creamos diccionario con lista de monedas y su valor en euros
lista_monedas = ['ETH','LTC','BNB','EOS','XLM','TRX','BTC','XRP','BCH','USDT','BSV','ADA']
precio_monedas = []

for moneda in lista_monedas:
    precio_monedas.append(round(data['data'][f"{moneda}"]['quote']['EUR']['price'], 2))

dict_monedas = dict(zip(lista_monedas,precio_monedas))
print(dict_monedas)

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
    return render_template('index.html', dict_monedas=dict_monedas)

# Renderizado registro
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    
    # Formulario compra
    form = CompraForm(request.form)
    
    if request.method == 'POST':
        print("El methodo ha sido post!")
        if form.validate():
            print("Se ha validado!")
            # consulta('INSERT INTO users (password, email, fecha_alta) VALUES (?, ? ,? );', 
            #         (
            #             form.password_registre.data,
            #             form.email_registre.data,
            #             date.today(),
            #         )
            # )

            return redirect(url_for('purchase'))
        else:
            return render_template("purchase.html", form=form)
            
    return render_template("purchase.html", form=form)

