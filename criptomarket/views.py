from criptomarket import app
from criptomarket.forms import *
from flask import render_template, request, url_for, redirect, flash, Response
import sqlite3
from datetime import date, time, datetime
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# Atajo conexión base de datos y API
DBFILE = app.config['DBFILE']
API_KEY = app.config['API_KEY']

def consultaApi(fromMoneda, toMoneda, cantidad=1):
# Conexion con la API y parámetros
    url = f"https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={cantidad}&symbol={fromMoneda}&convert={toMoneda}&CMC_PRO_API_KEY={API_KEY}"
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    # Recolecta datos JSON y Control errores
    try:
        response = session.get(url, params=None)
        data = json.loads(response.text)
            
        valor_from = round(data['data']['amount'], 10)
        valor_to = round(data['data']['quote'][toMoneda]['price'], 10)
    
        
    except (ConnectionError, Timeout, TooManyRedirects, KeyError) as errores:
        raise BufferError

    return valor_from, valor_to

# print(consultaApi('EUR', 'BTC'))

# Función de la query a la BD
def consulta(query, params=()):

    conn = sqlite3.connect(DBFILE)
    c = conn.cursor()

    c.execute(query, params)
    conn.commit()

    filas = c.fetchall()
    conn.close()

    if len(filas) == 0:
        return filas
    else:
        columnNames = []
        for columnName in c.description:
            columnNames.append(columnName[0])

        listaDeDiccionarios = []

        for fila in filas:
            d = {}
            for ix, columnName in enumerate(columnNames):
                d[columnName] = fila[ix]
            listaDeDiccionarios.append(d)

        return listaDeDiccionarios

def calcularWallet():

    # 30.000€ iniciales para invertir
    wallet = {'EUR':30000, 'ETH':0, 'LTC':0,'BNB':0,'EOS':0,'XLM':0,'TRX':0,'BTC':0,'XRP':0,'BCH':0,'USDT':0,'BSV':0,'ADA':0}

    lista_movimientos = consulta('SELECT * FROM movements;')

    # Suma y resta calculando el valor de tu wallet
    for movimiento in lista_movimientos:
        wallet[movimiento['from_moneda']] = wallet[movimiento['from_moneda']] - movimiento['from_cantidad']
        wallet[movimiento['to_moneda']] = wallet[movimiento['to_moneda']] + movimiento['to_cantidad']
        
    if wallet['EUR'] <= 0:
        print('Tu saldo actual en € es igual a 0')

    return wallet

wallet = calcularWallet()

# Renderizado home
@app.route('/')
def index():

    # El teu wallet
    wallet = calcularWallet()
    monedas_con_credito = {}

    for valor in wallet:
        if wallet[valor] > 0:
            monedas_con_credito[valor] = wallet[valor]

    # Llista de monedes i valors a la home
    lista_monedas = ['ETH','LTC','BNB','EOS','XLM','TRX','BTC','XRP','BCH','USDT','BSV','ADA']
    valor_todas = []

    lista_movimientos = consulta('SELECT * FROM movements;')

    for moneda in lista_monedas:
        valor_todas.append(consultaApi(moneda, 'EUR'))
    
    dict_monedas = dict(zip(lista_monedas,valor_todas))

    return render_template('index.html', dict_monedas=dict_monedas, lista_movimientos=lista_movimientos, wallet=monedas_con_credito)

# Renderizado registro
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    
    # Formulario compra
    form = CompraForm(request.form)

    # Iniciamos variables
    wallet = calcularWallet()
    cantidad_obtenida = 0
    precio_unidad = 0
    calculando = False

    # El teu wallet
    monedas_con_credito = {}

    for valor in wallet:
        if wallet[valor] > 0:
            monedas_con_credito[valor] = wallet[valor]   

    # Seleccion de monedas con fondos
    monedas_disponibles = []
    for moneda in wallet:
        if wallet[moneda] > 0:
            monedas_disponibles.append(moneda)
    form.moneda_compra_from.choices = monedas_disponibles

    if request.method == 'POST':
        print("El methodo ha sido post!")

        if form.validate():
            
            cantidad_obtenida = consultaApi(form.moneda_compra_from.data, form.moneda_compra_to.data, form.cantidad_compra.data)[1]

            precio_unidad = consultaApi(form.moneda_compra_to.data, 'EUR', 1)[1]

            if form.moneda_compra_from.data != form.moneda_compra_to.data:

                if form.calcular_compra.data:

                    calculando = True

                    return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, moneda_to=form.moneda_compra_to.data, calculando=calculando, wallet=monedas_con_credito)
                
                elif form.confirmar_compra.data:
                    
                    if form.cantidad_compra.data > wallet[form.moneda_compra_from.data]:
                        flash("No tens suficienment crèdit. No s'ha registrat la compra.")
                        return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, moneda_to=form.moneda_compra_to.data, wallet=monedas_con_credito)
                    
                    else:

                        try:
                            # Registra movimiento en la database
                            consulta('INSERT INTO MOVEMENTS (date, time, from_moneda, from_cantidad, to_moneda, to_cantidad, valor_en_euros) VALUES (?, ?, ?, ?, ?, ?, ? );', 
                                    (
                                        str(date.today()),
                                        str(datetime.now().time().isoformat(timespec='seconds')),
                                        str(form.moneda_compra_from.data),
                                        float(form.cantidad_compra.data),
                                        str(form.moneda_compra_to.data),
                                        float(cantidad_obtenida),
                                        float(consultaApi(form.moneda_compra_from.data,'EUR',form.cantidad_compra.data)[1])
                                    )
                            )

                            flash("Compra efectuada correctament!")
                            
                            redirect(url_for("index"))
                        
                        except:
                            raise BufferError


                    return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, moneda_to=form.moneda_compra_to.data, wallet=monedas_con_credito)
            else:
                flash("La moneda de compra i venta no poden ser la mateixa.")
                return render_template("purchase.html", form=form, cantidad_obtenida=0, precio_unidad=0, wallet=monedas_con_credito)

        
        else:
            return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, wallet=monedas_con_credito)
            
    return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, wallet=monedas_con_credito)

@app.route('/status')
def status():
    
    lista_movimientos = consulta('SELECT * FROM movements;')

    valores_actuales = []
    for movimiento in lista_movimientos:
        valores_actuales.append(consultaApi(movimiento['to_moneda'],'EUR',movimiento['to_cantidad'])[1])

    valores_antiguos = []
    for movimiento in lista_movimientos:
        valores_antiguos.append(movimiento['valor_en_euros'])

    total_balance = (round(sum(valores_actuales) - sum(valores_antiguos), 2))

    inversion_total = consulta("SELECT SUM(from_cantidad) FROM movements where from_moneda='EUR';")[0]['SUM(from_cantidad)']

    return render_template("status.html", lista_movimientos=lista_movimientos, valores_actuales=valores_actuales, valores_antiguos=valores_antiguos, total_balance=total_balance, inversion_total=inversion_total)

@app.errorhandler(404)
def page_not_found(e):
    print("Error 404!")
    return render_template('404.html'), 404

@app.errorhandler(BufferError)
def buffer_error(e):
    print("Error de conexión con la API!")
    return render_template('apierror.html'), 404

@app.errorhandler(500)
def internal_error(error):
    print("Error interno!")
    return render_template('500.html'), 500



