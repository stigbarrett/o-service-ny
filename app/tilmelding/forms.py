from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, HiddenField, validators, RadioField, FileField, DateField
#from wtforms.fields.html5 import DateField  
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
#from wtforms.ext.sqlalchemy.orm import model_form
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileRequired
from werkzeug.utils import secure_filename
#from flask_babel import _, lazy_gettext as _l
#from app.models import User, Konkurrence, Grunddata, Klub, Medlemmer, Deltager, deltager_strak, Baner, PostBaner

class Tilmeld_flere(FlaskForm):
    loeb = StringField('Vaelg_loeb', id='loeb')
    submit_3 = SubmitField('Valg', id='submit_3')

class Tilmeld(FlaskForm):
    navn = StringField('navn')
    klub = StringField('klub')
    email = StringField('email')
    briknummer = StringField('briknummer')
    telefonnummer = StringField('telefonnummer')
    bane = StringField('bane')
    submit_1 = SubmitField('Vælg', id='submit_1')
    #submit_2 = SubmitField('Slut', id='submit_2')

class ret_tilmelding(FlaskForm):
    text = StringField('text')
    submit = SubmitField('submit_1', id='submit_1')

class tilfojGPXfil(FlaskForm):
    #loeb = StringField('skovID', id='loeb')
    loeb = SelectField('Løb:', validators=[DataRequired()], id='loeb')
    navn = StringField('navn')
    klub = StringField('klub')
    bane = StringField('bane')
    GPXfil = FileField()
    submit = SubmitField('Vælg', id='submit')

class alleTilmeldte(FlaskForm):
    loeb = SelectField('Løb:', validators=[DataRequired()], id='loeb')