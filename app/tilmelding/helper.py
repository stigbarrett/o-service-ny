from asyncio.windows_events import NULL
from sqlalchemy import desc 
from distutils.command.config import config
from flask_login import current_user
from sqlalchemy import desc
from app.models import Klubber, Post, User, Profile, Tilmeldte, konkurrence_data, Baner
from app import db
from base64 import b64encode
import os
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail
from datetime import date
#import app

SENDGRID_API_KEY="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"

def bruger_opl():
    pass
    #bruger = User.query.filter_by(id=current_user.id).first()
    #brugernavn = User.username
    #if not current_user.userpicture:
    #    path_profilpicture='default.png'
    #else:
    #    profilpicture = str(current_user.id) + ".png"
    #    profilepath = str(current_user.id) + "/"
    #    path_profilpicture = os.path.join(profilepath, profilpicture)
        #profilpicture = b64encode(current_user.userpicture).decode("utf-8")
        #profilpicture = current_user.userpicture
    
    #return path_profilpicture

def hent_alle_navne(aktivt_loeb):
    navneliste = []
    navne = db.session.query(Profile).all()
    tilmeldte = db.session.query(Tilmeldte).filter(Tilmeldte.konkurrence_id==aktivt_loeb).all()
    deltagere= []

    for tilmeldt in tilmeldte:
        deltagere.append(tilmeldt.profile_id)

    for navn in navne:
        profilid = navn.id
        if profilid not in deltagere:
            profil={}
            list_of_bool = [True for elem in navneliste if navn.navn in elem.values()]
            if any(list_of_bool):
                pass
            else:
                profil['id'] = navn.id
                profil['navn'] = navn.navn
                navneliste.append(profil)
    
    return navneliste


def hent_deltagerliste(profileId, lobid):
    deltagerliste = []
    for delt in db.session.query(Tilmeldte).filter(Tilmeldte.tilmelder_id==profileId, Tilmeldte.konkurrence_id==lobid).order_by(Tilmeldte.date_created.asc()).all():
        hver = {}
        hver['id'] = delt.id
        hver['Navn'] = delt.profile.navn
        hver['Klub'] = delt.klubber.Klubnavn
        hver['Bane'] = delt.bane
        hver['Brik'] = delt.profile.brik
        deltagerliste.append(hver)
    return deltagerliste


def hent_fuld_deltagerliste(lobid):
    deltagerliste = []
    for delt in db.session.query(Tilmeldte).filter(Tilmeldte.konkurrence_id==lobid).order_by(Tilmeldte.date_created.asc()).all():
        hver = {}
        hver['id'] = delt.id
        hver['Navn'] = delt.profile.navn
        hver['Klub'] = delt.klubber.Klubnavn
        hver['Bane'] = delt.bane
        hver['Brik'] = delt.profile.brik
        deltagerliste.append(hver)
    return deltagerliste

def hent_kort(id):
    lob = konkurrence_data.query.filter(konkurrence_data.id==id).all()
    if int(lob[0].kort_download) == 1:
        baner = Baner.query.filter(Baner.kokurrence_id==id, Baner.kort_navn_png!=None).order_by(Baner.banenavn).all()
        if len(baner) != 0:
            kortbane=[]
            kortene = []
            for kort in baner:
                kortet = {}
                kortstrip = {}
                kortet['beskrivelse'] = kort.bane_beskrivelse
                kortet['banenavn'] = kort.banenavn
                
                kortnavn = os.path.splitext(kort.kort_navn_png)[0]
                kort_stripnavn = (kortnavn.replace(" ", ""))
                kortet['stripnavn'] = kort_stripnavn
                kortstrip['fuldtnavn'] = kort.kort_navn_png
                kortstrip['havelaagenavn'] = kort_stripnavn
                kortstrip['Banenavn'] = kort.banenavn
                #fil = kortnavn + ".jpg"
                kort_sti = kort.path_filer
                #kortet['filen']=os.path.join(kort_sti, fil)
                #kortet['filen']=os.path.join(['UPLOAD_PATH'], kort.url, fil)
                kortet['filen'] = os.path.join(kort_sti, kort.kort_navn_png).replace("\\", "/")
                #kortet['filen']=str(kort.url) + "\\" + fil
                kortbane.append(kortstrip)
                kortene.append(kortet)
                kort = True 
        else:
            kortbane = ['Ingen']
            kortene = ['Ingen']
            kort = False
    else:
        kortbane = ['Ingen']
        kortene = ['Ingen']
        kort = False
    return kortbane, kortene, kort

def hent_klubber():
    #klubber = []
    klubber = {}
    for klub in db.session.query(Klubber):
        
        klubber[str(klub.id)] = klub.Klubnavn
        #klubber.append(hver)
    return klubber

def hent_alle_deltagerliste(loeb_id):
    
    lobid = 2
    lobklar = db.session.query(Tilmeldte).filter(Tilmeldte.konkurrence_id==loeb_id).all()
    klarelob = {}
    samlet=[]
    
    #klarelob[lob.skov]
    #loebere = db.session.query(Runners).filter(Runners.loeb_id==lob.id).all()
    deltagerliste = []
    
    
    for delt in lobklar:
        hver = {}
        hver['id'] = delt.id
        hver['Navn'] = delt.navn
        #hver['Klub'] = delt.klubber.Klubnavn
        #hver['Bane'] = delt.bane
        #hver['Brik'] = delt.profile.brik
        deltagerliste.append(hver)
    #klarelob[lob.skov] = deltagerliste
    #samlet.append(klarelob)
    return deltagerliste

def hent_pdf(id, path):
    lob = konkurrence_data.query.filter(konkurrence_data.id==id).all()
    for kort_alle in lob:
        kortbane=[]
        pdf = []
        for kort in kort_alle.filerne:
            kortet = {}
            #kortstrip = {}
            kortet['beskrivelse'] = kort.filbeskrivelse
            kortet['banenavn'] = kort.banenavn
            kortet['filnavn'] = kort.filnavn
            pdf_sti = kort.url
            kortet['filen']=os.path.join("website/static", path, pdf_sti, kort.filnavn).replace("\\", "/")
            #kortet['filen']= pdf_sti + "/" + fil
            #kortet['filen']=str(kort.url) + "\\" + fil
            #kortbane.append(kortstrip)
            pdf.append(kortet)
    return pdf

def hent_alle_tilmeldte(aktivt_loeb, profilId):
    tilmeldte_liste = []
   
    #alletilmeldte = db.session.query(Tilmeldte).filter(Tilmeldte.runners.loeb_id != 2).all()
    alletilmeldte = db.session.query(Tilmeldte).all()
    #er_tilmeldt = db.session.query(Runners).all()
    for tilmeldt in alletilmeldte:
        deltager = False
        deltager_ikke = False
        #for run in tilmeldt:
        if tilmeldt.konkurrence_id == aktivt_loeb:
            deltager = True
        else:
            deltager_ikke = True
        if deltager is False:
            hver_tilmeldt = {}
            hver_tilmeldt['id'] = tilmeldt.id
            hver_tilmeldt['navn'] = tilmeldt.navn
            tilmeldte_liste.append(hver_tilmeldt)
        
    return tilmeldte_liste

def hent_senst_tilmeldte(profileId, lobid):
    deltagerliste = []
    for delt in db.session.query(Tilmeldte).filter(Tilmeldte.profile_id==profileId, Tilmeldte.konkurrence_id==lobid).all():
        hver = {}
        hver['id'] = delt.id
        hver['navn'] = delt.navn
        deltagerliste.append(hver)
    return deltagerliste