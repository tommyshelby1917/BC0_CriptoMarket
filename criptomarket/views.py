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

def convertirApi(fromMoneda, toMoneda, cantidad=1):
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
        print(errores)

    return valor_from, valor_to

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

    try:
        lista_movimientos = consulta('SELECT * FROM movements;')
    except:
        raise MemoryError

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

    try:
        lista_movimientos = consulta('SELECT * FROM movements;')
    except:
        raise MemoryError

    for moneda in lista_monedas:
        valor_todas.append(convertirApi(moneda, 'EUR'))
    
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
    comprar = False

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
            
            cantidad_obtenida = convertirApi(form.moneda_compra_from.data, form.moneda_compra_to.data, form.cantidad_compra.data)[1]

            precio_unidad = convertirApi(form.moneda_compra_to.data, 'EUR', 1)[1]

            if form.moneda_compra_from.data != form.moneda_compra_to.data:

                if form.calcular_compra.data:

                    if form.cantidad_compra.data > wallet[form.moneda_compra_from.data]:

                        flash("Pots consultar el canvi de moneda, però no tens suficientment crèdit per fer la compra.")
                        return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, moneda_to=form.moneda_compra_to.data, wallet=monedas_con_credito, comprar=comprar)

                    else:

                        calculando = True
                        comprar = True

                        return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, moneda_to=form.moneda_compra_to.data, calculando=calculando, wallet=monedas_con_credito, comprar=comprar)
                
                elif form.confirmar_compra.data:
                    
                    if form.cantidad_compra.data > wallet[form.moneda_compra_from.data]:
                        flash("No tens suficienment crèdit. No s'ha registrat la compra.")
                        return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, moneda_to=form.moneda_compra_to.data, wallet=monedas_con_credito, comprar=comprar)
                    
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
                                        float(convertirApi(form.moneda_compra_from.data,'EUR',form.cantidad_compra.data)[1])
                                    )
                            )

                            flash("Compra efectuada correctament!")
                            
                            redirect(url_for("index"))
                        
                        except:
                            raise MemoryError


                    return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, moneda_to=form.moneda_compra_to.data, wallet=monedas_con_credito, comprar=comprar)
            else:
                flash("La moneda de compra i venta no poden ser la mateixa.")
                return render_template("purchase.html", form=form, cantidad_obtenida=0, precio_unidad=0, wallet=monedas_con_credito, comprar=comprar)

        
        else:
            return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, wallet=monedas_con_credito, comprar=comprar)
            
    return render_template("purchase.html", form=form, cantidad_obtenida=cantidad_obtenida, precio_unidad=precio_unidad, wallet=monedas_con_credito, comprar=comprar)

@app.route('/status')
def status():

    try:
        lista_movimientos = consulta('SELECT * FROM movements;')
    except:
        raise MemoryError

    # Wallet de criptomonedas sin los euros
    wallet = calcularWallet()
    del wallet['EUR']
    criptowallet = {}
    for valor in wallet:
        if wallet[valor] > 0:
            criptowallet[valor] = wallet[valor]
    
    
    # Una lista con los valores en euros de cada wallet que tienes
    valor_euros = []
    for cripto in criptowallet:
        valor_euros.append(convertirApi(cripto,'EUR',criptowallet[cripto])[1])

    # La suma en euros de todas las monedas que tienes
    total_cripto_valores = sum(valor_euros)

    # Euros atrapados en inversion
    euros_atrapados = 0
    de_euros = 0
    a_euros = 0
    
    if consulta("SELECT SUM(from_cantidad) FROM movements where from_moneda='EUR';")[0]['SUM(from_cantidad)'] == None:
        de_euros = 0
    else:
        de_euros = consulta("SELECT SUM(from_cantidad) FROM movements where from_moneda='EUR';")[0]['SUM(from_cantidad)']
    
    if consulta("SELECT SUM(to_cantidad) FROM movements where to_moneda='EUR';")[0]['SUM(to_cantidad)'] == None:
        a_euros = 0
    else:
        a_euros = consulta("SELECT SUM(to_cantidad) FROM movements where to_moneda='EUR';")[0]['SUM(to_cantidad)']

    euros_atrapados = euros_atrapados - de_euros + a_euros

    # Estado actual de la inversión
    estado_inversion = total_cripto_valores - abs(euros_atrapados)  
    
    return render_template("status.html", lista_movimientos=lista_movimientos, valor_euros=valor_euros, criptowallet=criptowallet, total_cripto_valores=total_cripto_valores, euros_atrapados=euros_atrapados, estado_inversion=estado_inversion)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(BufferError)
def buffer_error(e):
    print("Error de conexión con la API!")
    return render_template('apierror.html'), 500

@app.errorhandler(500)
def internal_error(error):
    print("Error interno!")
    return render_template('500.html'), 500

@app.errorhandler(TypeError)
def type_error(error):
    print("Error interno!")
    return render_template('apierror.html'), 500

@app.errorhandler(MemoryError)
def memory_error(error):
    print("Error de conexion con la base de datos!")
    return render_template("dberror.html"), 500



