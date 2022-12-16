from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, HiddenField, validators, RadioField, FileField
from wtforms.fields.html5 import DateField  
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileRequired
from werkzeug.utils import secure_filename
from flask_babel import _, lazy_gettext as _l
from app.models import User, konkurrence_data, Klubber, Tilmeldte, Baner, Profile


def enabled_klubber():
    AlleKlubber = Klubber.query.all()
    return AlleKlubber

#def enabled_grunddata():
#    AlleGrunddata = Grunddata.query.all()
#    return AlleGrunddata

def enabled_konkurrencer():
    AlleKonkurrencer = konkurrence_data.query.all()
    return AlleKonkurrencer

def enabled_baner():
    AlleBaner = Baner.query.all()
    return AlleBaner

class BeregnForm(FlaskForm):
    submit_1 = SubmitField('Send', id='Submit_1')

class klarmelde(FlaskForm):
    loeb = StringField('skovID')
    submit = SubmitField('Klarmeld', id='Submit')

class OpretLoeb(FlaskForm):
    skov = StringField('skov')
    klubber = SelectField('klub', choises=[('True', 'Ja')])
    dato = DateField('dato')
    type = StringField('type')
    ansvarlig = StringField('Ansvarlig')
    andet = StringField('andet')
    emitenheder = RadioField('emitenheder', choises=[('True', 'Ja'), ('False', 'Nej')])
    klarmeldt = RadioField('klarmeldt', choises=[('True', 'Ja'), ('False', 'Nej')])
    resultat = RadioField('resultat', choises=[('True', 'Ja'), ('False', 'Nej')])
    submit_1 = SubmitField('Vælg', id='submit_1')

class TilfojKort(FlaskForm):
    loeb = StringField('skovID', id='loeb')
    bane = StringField('Bane')
    beskrivelse = StringField('Beskrivelse')
    #kort = FileField(validators=[FileRequired()])
    file = FileField()
    submit = SubmitField('Vælg', id='submit')

class AdminForm(FlaskForm):
    "Opsætnings form"
    KonkurrenceType = StringField(_l('KonkurrenceType', validators=[DataRequired()]))
    Skov = StringField(_l('Skov/Navn', validators=[DataRequired()]))
    Dato = DateField(_l('Dato', validators=[DataRequired()]))
    #Path = StringField(_l('Path', validators=[DataRequired()]))
    Mappenavn = StringField(_l('Mappenavn', validators=[DataRequired()]))
    Klub = QuerySelectField(query_factory=enabled_klubber, get_label='langtnavn', 
                        allow_blank=True, blank_text=(u'Klik for at vælge'))
    #Grunddata = QuerySelectField(query_factory=enabled_grunddata, get_label='aar', 
    #                    allow_blank=True, blank_text=(u'Klik for at vælge'))
    submit = SubmitField(_l('Indsend'))


class BeregnForm(FlaskForm):
    "Beregner form"
    KonKur = QuerySelectField(query_factory=enabled_konkurrencer, get_label='mappenavn', 
                        allow_blank=True, blank_text=(u'Klik for at vælge'))
    submit = SubmitField(_l('Omform'))
    submit1 = SubmitField(_l('Tilret'))
    submit2 = SubmitField(_l('Indlæs'))
    submit3 = SubmitField(_l('Test Mail'))
    submit4 = SubmitField(_l('Test export'))

class Statistik(FlaskForm):
    form_name = HiddenField('Form Name')
    statistik = SelectField('Statistik:', choices=[('klubber', 'Klubber'), ('delt1', 'Deltager pr. bane'), ('delt2', 'Deltager pr. klub')], id='select_statistik')
    submit = SubmitField(_l('Vælg'))

class Straktider(FlaskForm):
    form_name1 = HiddenField('Form Name')
    konkurrence = SelectField('Konkurrence:', validators=[DataRequired()], id='select_konkurrence')
    bane = SelectField('Bane:', validators=[DataRequired()], id='select_bane')
    art = RadioField('Hvad:', validators=[DataRequired()], choices=[('resultat', 'Resultater'),('straktider', 'Stræktider')], default='resultat' ,id='select_type')
    submit1 = SubmitField('Vælg', id='vaelg_resultat')

class Point(FlaskForm):
    form_name2 = HiddenField('Form Name')
    banepoint = SelectField('Banepoint', validators=[DataRequired()], choices=[('Bane 1', 'Bane 1'), ('Bane 2', 'Bane 2'), ('Bane 3', 'Bane 3'), ('Bane 4', 'Bane 4'), ('Bane 5', 'Bane 5')], id='select_bane_point')
    #banepoint = SelectField('Banepoint', validators=[DataRequired()], id='select_bane_point')
    submit2 = SubmitField('Vælg Bane')
    
class brugerbaner(FlaskForm):
    form_name1 = HiddenField('Form Name')
    bruger = SelectField('Bruger:', validators=[DataRequired()], id='select_brugerbaner')
    #bane = SelectField('Bane:', validators=[DataRequired()], id='select_bane')
    #art = RadioField('Hvad:', validators=[DataRequired()], choices=[('resultat', 'Resultater'),('straktider', 'Stræktider')], default='resultat' ,id='select_type')
    #submit3 = SubmitField('Vælg Løber')

class findFil(FlaskForm):
    form_name1 = HiddenField('Form Name')
    resultat = FileField(validators=[FileRequired()])
    submit1 = SubmitField('Upload resultat fil')

class bearbejdResultatKlub(FlaskForm):
    form_name2 = HiddenField('Form Name')
    klubnavn_fil = StringField(_l('klubnavnFil'))
    klubnavn_DB = StringField(_l('klubnavnDB'))
    vurderet = SelectField('vurderet', validators=[DataRequired()], choices=[('1', 'OK'), ('2', 'Ej OK')], id='select_vurderet')
    submit2 = SubmitField('Næste Klub')

class bearbejdResultatDeltager(FlaskForm):
    form_name3 = HiddenField('Form Name')
    navn_fil = StringField(_l('navnFil'))
    navn_DB = StringField(_l('navnDB'))
    navn_tilrettet = StringField(_l('navnTilrettet'))
    #navn_valgt = RadioField('Hvad:', validators=[DataRequired()], choices=[('fil', 'Navn i fil'),('DB', 'Navn i DB'),('rettet','Til Rettet')], default='DB', id='select_type')
    navn_valgt = RadioField('Hvad:', validators=[DataRequired()], choices=[('negativ', 'Samme person?'),('fil', 'Navn i fil'),('DB', 'Navn i DB'),('rettet','Tilrettet')], default='DB', id='select_type')
    submit3 = SubmitField('Næste Navn')

class XMLStraktider(FlaskForm):
    form_name1 = HiddenField('Form Name')
    konkurrence_felt = SelectField('Konkurrence:', validators=[DataRequired()], id='select_konkurrence')
    bane = SelectField('Bane:', validators=[DataRequired()], id='select_bane')
    #art = RadioField('Hvad:', validators=[DataRequired()], choices=[('resultat', 'Resultater'),('straktider', 'Stræktider')], default='resultat' ,id='select_type')
    #submit1 = SubmitField('Vælg', id='vaelg_resultat')

class opload_resultat(FlaskForm):
    form_name = HiddenField('Form Name')
    k_felt = StringField(_l('reultat_fil'))

class tilfojGPXfil(FlaskForm):
    #loeb = StringField('skovID', id='loeb')
    loeb = SelectField('Løb:', validators=[DataRequired()], id='loeb')
    navn = StringField('navn')
    klub = StringField('klub')
    bane = StringField('bane')
    GPXfil = FileField()
    submit = SubmitField('Vælg', id='submit')
