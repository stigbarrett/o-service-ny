from sqlalchemy import and_
from distutils.command.config import config
from flask_login import current_user
from app.models import Klubber, Post, User, Profile, Tilmeldte, konkurrence_data, Baner
from app import db
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

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False


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

def change(s, a, b):
    s[b], s[a] = s[a], s[b]

def distance_from(loc1,loc2): 
    dist=hs.haversine(loc1,loc2,unit='m')
    return round(dist,2)

def checkDir(check_dir):
    if os.path.isdir(check_dir) == True:
        shutil.rmtree(check_dir)
        os.mkdir(check_dir)
    else:
        os.mkdir(check_dir)

def find_kmz(pathInd, filename):
    #filepath = [f for f in os.listdir(pathInd) if f.endswith('.kmz')]
    filepath = os.path.join(pathInd, filename)
    return filepath

def unzip(file, pathTemp):
    with zipfile.ZipFile(file, 'r') as zip:
        for file in zip.namelist():
            zip.extract(file, pathTemp)
        fileOmdoeb = 'Doc.kml'
        if os.path.exists(os.path.join(pathTemp, fileOmdoeb)):
            os.rename(os.path.join(pathTemp, fileOmdoeb), os.path.join(pathTemp, fileOmdoeb.lower()))
        status = 1
    return status

def slet(pathTemp):
    D = os.path.join(pathTemp, 'files')
    T = ".SVG"
    filtered_files = []
    files_in_directory = os.listdir(D)
    for files in files_in_directory:
        if files.upper().endswith(T):
            filtered_files.append(files)

    for files in filtered_files:
        path_to_file = os.path.join(D, files)
        os.remove(path_to_file)

    status = 2
    return status

def omdoeb(pathUd, pathTemp):
    D = os.path.join(pathUd, 'files')
    E = os.path.join(pathTemp, 'files')
    T = ".JPG"
    #newfilename = "tile_0_0.jpg"
    filtered_files = []
    files_in_directory = os.listdir(E)
    for file in files_in_directory:
        if file.upper().endswith(T):
            filtered_files.append(file)

    for a, file in enumerate(filtered_files):
        if os.path.isdir(os.path.join(pathUd, 'files')) == False:
            os.mkdir(os.path.join(pathUd, 'files'))
        newfilename = "tile_" + str(a) + ".jpg"
        path_to_newFile = os.path.join(D, newfilename)
        path_to_file = os.path.join(E, file)
        os.rename(path_to_file, path_to_newFile)
    
    status = 3
    return status

def postKoordinater(stat_path):
    originalFil = os.path.join(stat_path, 'doc.kml')
    with open(originalFil, 'rt', encoding='utf8') as f:
        doc = parser.parse(f)
        root = doc.getroot()
        
        kontrols = root.attrib.values()
        
        if "Condes version 10" not in kontrols[1]:
            status = 10
            return status
    
    folder = doc.getroot().Folder.Folder
    loebnavnTemp = str(doc.getroot().Folder.name)
    baneNavn = str(folder.Folder.name)
    postKoordinater = {}
    kortopl = []
    for pm2 in folder:
        kort_bounds = {}
        kort_bounds['kortnavn'] = str(pm2.name)[0:8]
        temp_forhold = str(pm2.name)[-7:-1]
        if temp_forhold[0:1] == ':':
            kort_bounds['forhold'] = str(temp_forhold[1:7])
        else:
            kort_bounds['forhold'] = str(temp_forhold)

        kort_bounds['min_lon'] = str(pm2.GroundOverlay.LatLonBox.west)
        kort_bounds['max_lon'] = str(pm2.GroundOverlay.LatLonBox.east)
        kort_bounds['min_lat'] = str(pm2.GroundOverlay.LatLonBox.north)
        kort_bounds['max_lat'] = str(pm2.GroundOverlay.LatLonBox.south)
        kort_bounds['kortfil'] = str(pm2.GroundOverlay.Icon.href)
        banenavnListe = []
        banelaengdeListe = []
        
        for pm1 in pm2.Folder:
            baneNavn = pm1.name
            banelaengde = 0
            postKoordinaterListe = []
            x=0
            for placemarks in pm1.Folder.Placemark:
                if x == 0:
                    tempafstand = 0
                else:
                    foercoor = coordinates_conv
                postKoordinatesDict = {}
                name_pmTemp = {}
                name_pmTemp = placemarks.attrib
                name_pm = name_pmTemp['id']
                findStart = str(name_pm).find('S')
                findMaalM = str(name_pm).find('M')
                findMaalF = str(name_pm).find('F')
                findOvergang = str(name_pm).find('T')
                if findStart != -1:
                    name_pm = "S1"
                if findMaalM != -1 or findMaalF != -1:
                    name_pm = "F1"

                if findOvergang == -1:
                    coordinates = []
                    coordinates_conv = []
                    coordinates = str((placemarks.Point.coordinates)).split(',')
                    coordinates_conv.append(float(coordinates[1])) 
                    coordinates_conv.append(float(coordinates[0]))
                    
                    if x == 0 or name_pm == "F1":
                        postKoordinatesDict["Postnr"] = 0
                        if name_pm == "F1":
                            tempafstand = distance_from(foercoor, coordinates_conv)
                    else:
                        postKoordinatesDict["Postnr"] = x
                        tempafstand = distance_from(foercoor, coordinates_conv)
                    
                    banelaengde = banelaengde + tempafstand
                    postKoordinatesDict["Post"] = name_pm
                    postKoordinatesDict["coor"] = coordinates_conv
                    postKoordinaterListe.append(postKoordinatesDict)
                    x=x+1
                postKoordinater[str(baneNavn)] = postKoordinaterListe
            banenavnListe.append(str(baneNavn))
            banelaengdeListe.append(round(banelaengde, 0))
        kort_bounds['banelaengde'] = banelaengdeListe
        kort_bounds['baneliste'] = banenavnListe
        kortopl.append(kort_bounds)
    kortoplysninger = {}
    kortoplysninger['loebnavn'] = loebnavnTemp
    kortoplysninger['kort'] = kortopl

    #postKoordinatFilNavn = 'baner.json'
    #kortGrundoplysningerFilNavn = 'kortOplysninger.json'
    kontrolJson = json.dumps(postKoordinater, ensure_ascii=False)
    
    #kortGrundOplysninger = json.dumps(kortoplysninger, ensure_ascii=False)
    kortGrundOplysninger = json.dumps(kortopl, ensure_ascii=False)

    #with open(os.path.join(stat_path, postKoordinatFilNavn), 'w', encoding='utf8') as kontrolSkriv:
    #    kontrolSkriv.write(kontrolJson)
    
    #with open(os.path.join(stat_path, kortGrundoplysningerFilNavn), 'w', encoding='utf8') as oplSkriv:
    #    oplSkriv.write(kortGrundOplysninger)
    
    returData = {}
    returData['kortoplysninger'] = kortoplysninger
    returData['kontrolJson'] = kontrolJson
    returData['kortGrundOplysninger'] = kortGrundOplysninger

    #return kortoplysninger
    return returData

def checkDir(check_dir):
    if os.path.isdir(check_dir) == True:
        shutil.rmtree(check_dir)
        os.mkdir(check_dir)
    else:
        os.mkdir(check_dir)

def rydOp(rydop_dir):
    if os.path.isdir(rydop_dir) == True:
        shutil.rmtree(rydop_dir)

def dan_KMZ_coor(stat_path, filename):
    dannykml_var = postKoordinater(stat_path)
    slet(stat_path)
    return dannykml_var

def hent_kort(loeb_id):
    lob = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).all()
    if int(lob[0].kort_download) == 1:
        baner = Baner.query.filter(and_(Baner.kokurrence_id==loeb_id, Baner.kort_navn_pdf.is_not(None))).order_by(Baner.banenavn).all()
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
