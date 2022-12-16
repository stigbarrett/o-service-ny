from app import db
#from app.models import Klub, Grunddata, Konkurrence, Baner, PostBaner, deltager_strak, Deltager, Medlemmer, baneresultat, konkurrence_data
from app.models import Klubber
import time
from flask import jsonify
from datetime import datetime, date
from sqlalchemy import and_
from operator import itemgetter
import json

def hentResKolonner():
    Kolonner = []
    Placering = {}
    Status = {}
    Navn = {}
    Tid = {}
    Point = {}
    Klub = {}

    Placering['field'] = "Placering"
    Placering['width'] = 100
    Kolonner.append(Placering)

    Status['field'] = "Status"
    Status['width'] = 100
    Kolonner.append(Status)

    Navn['field'] = "Navn"
    Navn['width'] = 160
    Kolonner.append(Navn)

    Klub['field'] = "Klub"
    Klub['width'] = 160
    Kolonner.append(Klub)

    Tid['field'] = "Tid"
    Tid['width'] = 90
    Kolonner.append(Tid)

    Point['field'] = "Point"
    Point['width'] = 80
    Kolonner.append(Point)

    return Kolonner

def hentStrakKolonner(postbeskrivelser):
    antalPoster = len(postbeskrivelser)
    Kolonner = []
    TempResultat = {}
    Navn = {}
    Samlet = {}

    #postcode1 = detkomretur[0]['Splittid']
    Navn['field'] = "Navn"
    Navn['pinned'] = "left"
    Navn['width'] = 140
    Navn['filter'] = 'agSetColumnFilter'
    Navn['menuTabs'] = ['filterMenuTab']
    Kolonner.append(Navn)

    Samlet['field'] = "Samlet"
    Samlet['pinned'] = "left"
    Samlet['width'] = 80
    Samlet['suppressMenu'] = True
    Kolonner.append(Samlet)

    #x = 0
    for ii in range(antalPoster):
        postnr = str(postbeskrivelser[ii])
        #if ii + 1 < 10:
        #    postnr = "0" + str(ii+1) + '-' + str(postcode1[ii]['kontrolkode'])
        #else:
        #    postnr = str(ii + 1) + '-' + str(postcode1[ii]['kontrolkode'])

        TempResultat['field'] = postnr
        TempResultat['width'] = 90
        TempResultat['suppressMenu'] = True
        Kolonner.append(TempResultat)
        TempResultat = {}
        #x = x + 1
    return Kolonner

def hent_klubber():
    #klubber = []
    klubber = {}
    for klub in db.session.query(Klubber):
        
        klubber[str(klub.id)] = klub.Klubnavn
        #klubber.append(hver)
    return klubber