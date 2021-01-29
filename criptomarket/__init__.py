from flask import Flask


app = Flask(__name__, instance_relative_config=True, static_url_path='/static') # La configuracion la meteremos a traves de un fichero. config.py
app.config.from_object('config')

from criptomarket import views