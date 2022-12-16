from sqlalchemy import and_
from distutils.command.config import config
from flask_login import current_user
from app import db
from app.administration import bp
from app.models import Klubber, Post, User, Profile, Tilmeldte, konkurrence_data, Baner
from base64 import b64encode
from lxml import etree
from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import ATOM_ElementMaker as ATOM
from pykml.factory import GX_ElementMaker as GX
from pykml import parser
import os
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail
from datetime import date
#import app
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import haversine as hs
import datetime
import time
from datetime import datetime
from datetime import timezone
import folium
import lxml
import csv
from gpx_converter import Converter
from operator import itemgetter
import json
import zipfile
import shutil
import datetime


def find_result(correct, reduced_user_inputs, reduced_user_time_inputs):
    for idx, user_input in enumerate(reduced_user_inputs):
        if correct == user_input:
            # Vi fandt resultatet returner mindre set
            result_time = reduced_user_time_inputs[idx]
            return {'result': correct, 'result_time': result_time, 'reduced_user_time_inputs': reduced_user_time_inputs[idx+1:], 'reduced_user_inputs': reduced_user_inputs[idx+1:]}
    # Vi fandt ikke resultatet returner samme set
    #return {'result': -1, 'result_time': -1, 'reduced_user_time_inputs': reduced_user_time_inputs, 'reduced_user_inputs': reduced_user_inputs}
    return {'result': correct, 'result_time': "-", 'reduced_user_time_inputs': reduced_user_time_inputs, 'reduced_user_inputs': reduced_user_inputs}

#def test_splittider(kontroller, tider, pathcorrect):
def test_splittider(Deltager, bane_fra_kmz):
    
    #with open(pathcorrect, 'r', encoding='utf8') as f1:
    BaneCorrect = Baner.query.filter(Baner.id==bane_fra_kmz).first()
    correct = json.loads(BaneCorrect.post_gpx)
    #correct = json.load(f1)
    correct_inputs = []
    for postcorrect in correct:
        if postcorrect['Post'] == "S1" or postcorrect['Post'] == "F1":
            pass
        else:
            correct_inputs.append(int(postcorrect['Post']))

    #fast = OrderedDict(splittider_temp)
    #user_post_inputs = list(fast)
    user_post_inputs = [int(i) for i in Deltager['Kontroller']]
    #user_time_inputs = list(fast.values())
    user_time_inputs = [int(i) for i in Deltager['Tider']]
    reduced_user_inputs = user_post_inputs
    reduced_user_time_inputs = user_time_inputs
    validated_post_inputs = []
    validated_time_inputs = []
    slutprodukt = {}
    endeligprodukt = []
    x = 1
    for correct in correct_inputs:
        result = find_result(correct, reduced_user_inputs, reduced_user_time_inputs)
        reduced_user_inputs = result['reduced_user_inputs']
        reduced_user_time_inputs = result['reduced_user_time_inputs']
        validated_post_inputs.append(result['result'])
        validated_time_inputs.append(result['result_time'])
        slutprodukt['post_navn']='Post'+ str(x)
        slutprodukt['postnr'] = x
        slutprodukt['postkode'] = str(result['result'])
        slutprodukt['tid_til_ialt_sek'] = str(result['result_time'])
        if str(result['result_time']) == '-':
            slutprodukt['status'] = 'ejOK'
            slutprodukt['Status_id'] = 0
        else:
            slutprodukt['status'] = 'OK'
            slutprodukt['Status_id'] = 1
        #if x <= 9:
        #    slutprodukt['0' + str(x) + '-' + str(result['result'])] = str(result['result_time'])
        #else:
        #    slutprodukt[str(x) + '-' + str(result['result'])] = str(result['result_time'])
        endeligprodukt.append(slutprodukt)
        slutprodukt = {}
        x = x + 1

    return endeligprodukt


def baner(indholdList, path):
    '''Danner banedata. Bane nummer og poster på bane. Skriver fil med banens indhold'''

    Poster = dict()
    Test = dict()
    kontroller = []
    for y in range(len(indholdList)):
        if y == 1:
            Bane = indholdList[y]
            Bane = Bane[0:6]
        elif y > 1 and y < len(indholdList) - 1:
            Postnr = "Post " + (str(y - 1))
            Poster[Postnr] = indholdList[y]
            Test[Bane] = Poster
            kontroller.append(indholdList[y])
    filnavn = Bane + '.json'
    #endeligpath = os.path.join(path, mappe)
    with open(os.path.join(path, filnavn), 'w', encoding='utf8') as kontrolSkriv:
            kontrolJson = json.dumps(kontroller, ensure_ascii=False)
            kontrolSkriv.write(kontrolJson)

    return Bane, Test

def SaetStatus(indholdList, Bane):
    ''' Danner status data for løber '''
    indholdList.insert(0, Bane)
    if str(indholdList[1]) == ('"X"#Diskvalificeret'):
        indholdList.insert(1, "ejOK")
        #status = 3
        status = 0
    elif str(indholdList[1]) == ('"X"#Udgået'):
        indholdList.insert(1, "ejOK")
        #status = 2
        status = 0
    elif str(indholdList[1]) == ('"X"#Ingen sluttid'):
        indholdList.insert(1, "ejOK")
        #status = 4
        status = 0
    elif str(indholdList[1]) == ('"X"'):
        del indholdList[1]
        indholdList.insert(1, "OK")
        status = 1
    if status != 1:
        del indholdList[2]

    del indholdList[2]
    indholdList.insert(2, 0)
    indholdList.insert(-1, 0)
    return status

def delNavn(navn):
    opdelt = navn.split()
    efternavn = opdelt[-1]
    if len(opdelt) == 1:
        pass
    else:
        del opdelt[-1]
    seperator = ' '
    if len(opdelt) >= 1:
        fornavn = seperator.join(opdelt)
    else:
        fornavn = opdelt[-1]
    return fornavn, efternavn

def vendom(indholdList):
    navn = indholdList[3]
    opdelt = navn.split()
    efternavn = opdelt[0]
    del opdelt[0]
    seperator = ' '
    #print (navn)
    if len(opdelt) >= 1:
        fornavn = seperator.join(opdelt)
    else:
        fornavn = opdelt[-1]
    nytnavn = fornavn + " " + efternavn
    return nytnavn

def dump_to_XML(path, fil_navn, konkurrenceId):

    fil_resultat = os.path.join(path, fil_navn)
    efternavn_forst = 0
    BanerKlar = []
    #fil = (path + mappe + '\\' + fil_resultat)
    with open(fil_resultat, 'r', encoding="latin-1") as f:
        indhold = f.readlines()
        Deltager = dict()
        DeltagerKlar = []
        for i in range(len(indhold)):
            indholdList = [int(e) if e.isdigit() else e for e in indhold[i].split(',')]
            if str(indholdList[0]) == ('"R"'):
                Bane, Test = baner(indholdList, path)
                bane_fra_kmz = Baner.query.filter(Baner.kokurrence_id==konkurrenceId, Baner.banenavn==Bane).first()
                BanerKlar.append(Test)
                continue
            else:
                Statuskode = SaetStatus(indholdList, Bane)

            if str(indholdList[0]) == bane_fra_kmz.banenavn :
                Deltager['Bane'] = indholdList[0]
                Deltager['Bane'] = bane_fra_kmz.banenavn
                Deltager['BaneId'] = bane_fra_kmz.id
                Deltager['Status'] = indholdList[1]
                Deltager['Statuskode'] = Statuskode
                Deltager['Placering'] = ""
                if efternavn_forst == 1:
                    Deltager['Navn'] = vendom(indholdList)
                else:
                    fornavn, efternavn = delNavn(indholdList[3])
                    Deltager['Navn'] = indholdList[3]
                    Deltager['Fornavn'] = fornavn
                    Deltager['Efternavn'] = efternavn
                Deltager['Klub'] = indholdList[4]
                Deltager['Emit'] = indholdList[5]
                Deltager['Point'] = ""
                Straktider = (indholdList[6:len(indholdList) - 2])
                if len(indholdList) > 8 and len(Straktider) >= 3:
                    del Straktider[-1]
                    del Straktider[-1]
                    Deltager['Tid'] = str(datetime.timedelta(seconds=(Straktider[-1])))
                    Deltager['TidSek'] = Straktider[-1]
                    del Straktider[-1]
                    del Straktider[-1]

                    Strak = {}
                    Tid = 0
                    x = 1
                    kontrol = []
                    tid = []
                    postkontroller_fra_kmz = json.loads(bane_fra_kmz.post_gpx)
                    postkontrolListe = []
                    for postenhed in postkontroller_fra_kmz:
                        if postenhed['Post'] == "S1" or postenhed['Post'] == "F1":
                            pass
                        else:
                            postkontrolListe.append(int(postenhed['Post']))
                    
                    for y in range (len(Straktider)):
                        if y % 2 == 0:
                            ''' finder kontrol nummeret '''
                            Control = str('Post' + str(x) + ' - ' + str(Straktider[y]))
                            kontrol.append(str(Straktider[y]))
                            x = x + 1
                        else:
                            ''' finder tiden til kontrollen (sekunder) '''
                            Tid = Straktider[y]
                            tid.append(str(Straktider[y]))
                            Strak[Control] = Tid
                    Deltager['StrakTider'] = Strak
                    Deltager['Kontroller'] = kontrol
                    Deltager['Tider'] = tid
                else:
                    Deltager['Tid'] = 0
                    Deltager['StrakTider'] = ['0']
                    Deltager['Kontroller'] = ['0']
                    Deltager['Tider'] = 0
                    Deltager['TidSek'] = 0

                ''' Skriver deltager til et dictionarie som til slut skrives til json fil '''
                kontrol_postpassage = test_splittider(Deltager, bane_fra_kmz.id)
                Deltager['bearbejdet'] = kontrol_postpassage
                DeltagerKlar.append(Deltager)
            Deltager = dict()

        ''' Sorterer deltagerne efter bane og tid '''
        DeltagerKlar = sorted(DeltagerKlar, key = lambda i: (i['Bane'], i['Statuskode'], i['Tid']))
        #nyXMLfil = danXML(path, kun_filnavn, BanerKlar, DeltagerKlar)
        resultat = [DeltagerKlar]
    return resultat



def start_her(path, fil_navn, konkurrenceId):
    fil_resultater = dump_to_XML(path, fil_navn, konkurrenceId)

    return(fil_resultater)

