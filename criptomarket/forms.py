from criptomarket import app
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, IntegerField, DateField, StringField, FloatField, SubmitField, ValidationError, RadioField, validators, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import EmailField
import sqlite3

DBFILE = app.config['DBFILE']

class CompraForm(FlaskForm):
    moneda_compra_from = SelectField('En quina moneda vols pagar?', choices=['EUR','BTC'])
    moneda_compra_to = SelectField('Quina moneda vols comprar?', choices=['ETH','LTC','BNB','EOS','XLM','TRX','BTC','XRP','BCH','USDT','BSV','ADA'])
    cantidad_compra = FloatField('Quina cuantitat en €?', [validators.DataRequired()])
    calcular_compra = SubmitField('Calcular valor')
    confirmar_compra = SubmitField('Confirmar compra ✔️')