from criptomarket import app
from flask_wtf import FlaskForm
from wtforms import PasswordField, IntegerField, DateField, StringField, FloatField, SubmitField, ValidationError, RadioField, validators, BooleanField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import EmailField
import sqlite3

DBFILE = app.config['DBFILE']


class RegisterForm(FlaskForm):
    email_registre = EmailField('Correu electrònic', [validators.DataRequired()])
    password_registre = PasswordField('Contrasenya', [
        validators.DataRequired(), validators.EqualTo('confirm_registre', message='Les contrasenyes han de coincidir')
        ])
    confirm_registre = PasswordField('Repeteix la contrasenya')

class CompraForm(FlaskForm):
    moneda_compra = RadioField('Quina moneda?', choices=['BTC', 'ETH'])
    cantidad_compra = FloatField('Quina cuantitat en €?', [validators.DataRequired(), validators.Length(min=1, max=25)])