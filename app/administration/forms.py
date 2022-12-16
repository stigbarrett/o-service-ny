from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, HiddenField, RadioField, FileField, DateField
#from wtforms.fields.html5 import DateField  
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
#from wtforms.ext.sqlalchemy.orm import model_form
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileRequired
from werkzeug.utils import secure_filename
#from flask_babel import _, lazy_gettext as _l
#from app.models import User, Konkurrence, Grunddata, Klub, Medlemmer, Deltager, deltager_strak, Baner, PostBaner
from app.models import Klubber, konkurrence_data
from datetime import datetime, date, timedelta

idag_raw = date.today()

class BeregnForm(FlaskForm):
    submit_1 = SubmitField('Send', id='Submit_1')

class klarmelde(FlaskForm):
    loeb = StringField('skovID')
    submit = SubmitField('Klarmeld', id='Submit')

class Opret_Loeb(FlaskForm):
    skov = StringField('skov')
    klub = StringField('klub')
    dato = DateField('dato')
    type = StringField('type')
    andet = StringField('andet')
    emitenheder = RadioField('emitenheder', choices=[('True', 'Ja'), ('False', 'Nej')])
    klarmeldt = RadioField('klarmeldt', choices=[('True', 'Ja'), ('False', 'Nej')])
    kort_download = RadioField('kort', choices=[('True', 'Ja'), ('False', 'Nej')])
    file = FileField()
    #resultat = FileField(validators=[FileRequired()])
    submit_1 = SubmitField('Vælg', id='submit_1')

class TilfojKort(FlaskForm):
    form_name = HiddenField('TilfojKort')
    #loeb = StringField('skovID', id='loeb')
    loeb = SelectField('skovID', validators=[DataRequired()], id='loeb')
    #bane = StringField('Bane', id='bane')
    bane = SelectField('Bane', validators=[DataRequired()], id='bane')
    beskrivelse = StringField('Beskrivelse')
    #kort = FileField(validators=[FileRequired()])
    file = FileField()
    submit = SubmitField('Vælg', id='submit')

class tilfojKMZfil(FlaskForm):
    skov = StringField('skov')
    klub = StringField('klub')
    dato = DateField('dato')
    loeb = StringField('skovID', id='loeb')
    file = FileField()
    submit = SubmitField('Vælg', id='submit')

class retLoeb(FlaskForm):
    form_name = HiddenField('ret_loeb')
    loeb = SelectField('skovID', validators=[DataRequired()], id='loeb')
    klub = StringField('klub')
    dato = DateField('dato')
    type = StringField('type')
    andet = StringField('andet')
    emitenheder = RadioField('emitenheder', choices=[('True', 'Ja'), ('False', 'Nej')])
    klarmeldt = RadioField('klarmeldt', choices=[('True', 'Ja'), ('False', 'Nej')])
    kort_download = RadioField('kort', choices=[('True', 'Ja'), ('False', 'Nej')])
    submit_1 = SubmitField('Vælg', id='submit_1')

class indsend_resultat(FlaskForm):
    form_name = HiddenField('indsend_resultat')
    konkurrence = SelectField('konkurrence', validators=[DataRequired()], id='loeb')
    indberetter = StringField('indberetter', id='indberetter')
    klub = SelectField('klub', id='klub')
    type_konkurrence = SelectField('type', id='type', choices=[('eresult', 'eresult')])
    data_format = SelectField('format', id='format')
    o_track_link = StringField('otrack', id='otrack')
    resultatfil = FileField()
    submit_1 = SubmitField('Indsend', id='submit_1')