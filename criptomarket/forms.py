from criptomarket import app
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, IntegerField, DateField, StringField, FloatField, SubmitField, DecimalField, ValidationError, RadioField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
import sqlite3

class CompraForm(FlaskForm):
    moneda_compra_from = SelectField('En quina moneda vols pagar?')
    moneda_compra_to = SelectField('Quina moneda vols comprar?', choices=['EUR','ETH','LTC','BNB','EOS','XLM','TRX','BTC','XRP','BCH','USDT','BSV','ADA'])
    cantidad_compra = DecimalField('Quina cuantitat?', validators=[DataRequired(message="Has d'introduir un número."), NumberRange(min=0, max=99999, message='Debe ser un numero entre 0 y 99999')])
    calcular_compra = SubmitField('Calcular valor')
    confirmar_compra = SubmitField('Confirmar compra ✔️')

