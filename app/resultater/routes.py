from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, session, send_from_directory, send_file, Response
from flask_login import current_user, login_required
from app import db
from app.models import Klubber, Post, User, Profile, Tilmeldte, baneresultat, konkurrence_data, Baner, Poster 
from app.resultater import bp
#from app.resultater.controllerloeb import hent_sensteskov, hent_k, hent_klub, hentPoint, hentPointNy, hent_bruger_data, hent_statistik1, hent_statistik2, \
#    hent_statistik3, hentPointKolonner, hentPointKolonnerNy, hentStrakBane_data, hentStrakKolonner, hentResBane_data, hentResKolonnerGL, \
#        hent_bruger_kolonner, hent_ny_statistik1, hent_ny_statistik2, hent_ny_statistik3

from app.resultater.Omform import omdan
from app.resultater.resultat_helper import hentResKolonner, hentStrakKolonner, hent_klubber
from app.resultater.gpx_helper import start_gpx, map_create, map_create_flere
#from app.resultater.Navnetjek import NavneTjek
from app.resultater.forms import AdminForm, opload_resultat, tilfojGPXfil, BeregnForm, Straktider, Point, brugerbaner, Statistik, findFil, bearbejdResultatKlub, bearbejdResultatDeltager, XMLStraktider
import os
import json, codecs
import shutil
import tempfile
from pathlib import Path
#import zipfile
from zipfile import ZipFile
#from io import BytesIO
from werkzeug.utils import secure_filename
from os import listdir
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import haversine as hs
import datetime
import time
from datetime import date
from datetime import datetime
from datetime import timezone
import folium
from folium import plugins
import lxml
from operator import itemgetter, attrgetter
import math

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'kmz'}

#photos = UploadSet('photos', ALL)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/Base_resultater', methods=['GET', 'POST'])
def Base_resultater():
    form1 = XMLStraktider(form_name1='Straktider')
    return render_template('resultater/Base_resultater.html', form1=form1)

@bp.route('/resultater', methods=['GET', 'POST'])
def resultater():
    form1 = XMLStraktider(form_name1='Straktider')
    konkurrence1 = konkurrence_data.query.filter(konkurrence_data.konkurrenceType!='').order_by(konkurrence_data.id.desc()).first()
    #konkurrence2 = konkurrence1.pathKonkurrenceFiler
    #form1.konkurrence_felt.choices = [(str(row.id), row.konkurrence + '-' + str(row.konkurrenceDato)) for row in konkurrence_data.query.filter(konkurrence_data.konkurrenceType=='alm').order_by(konkurrence_data.id.desc()).all()]
    #form1.konkurrence_felt.choices = [(str(row.id), row.konkurrence + '-' + str(row.konkurrenceDatoStart)) for row in konkurrence_data.query.filter(konkurrence_data.konkurrenceType!='', konkurrence_data.konkurrenceDatoStart>= '2022-03-30').order_by(konkurrence_data.id.desc()).all()]
    loeb_alle = []
    loeb = {}
    #alle_loeb = [(str(row.id), row.konkurrence + '-' + str(row.konkurrenceDatoStart)) for row in konkurrence_data.query.filter(konkurrence_data.konkurrenceType!='', konkurrence_data.konkurrenceDatoStart>= '2022-03-30').order_by(konkurrence_data.id.desc()).all()]
    alle_loeb = konkurrence_data.query.order_by(konkurrence_data.konkurrenceDatoSlut.desc()).all()
    baner_alle = []
    bane_en = {}
    for lob in alle_loeb:
        loeb = {}
        loeb['id'] = int(lob.id)
        loeb['navn'] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDatoSlut)
        loeb_alle.append(loeb)
        alleBaner = Baner.query.filter(Baner.kokurrence_id==lob.id).all()
        for bane in alleBaner:
            bane_en = {}
            bane_en['id'] = bane.id
            bane_en['navn'] = str(bane.banenavn)
            baner_alle.append(bane_en)
        #with open(os.path.join(konkurrence2, "klasseListe.json"), "r") as file:
    #        manu = json.load(file)
    #        form1.bane.choices = [(i['Bane'], i['vaerdi']) for i in manu]
    
    
    #form1.bane.choices = [(row.id, row.banenavn) for row in Baner.query.filter(Baner.kokurrence_id==konkurrence1.id).all()]
    #if request.method == 'GET':
    return render_template('resultater/resultater.html', form1=form1, loeb_alle=loeb_alle, baner_alle=baner_alle)
    #return redirect('resultater.resultater')


@bp.route('/_get_XMLbaner/<konkurrence>', methods=['GET', 'POST'])
def _get_XMLbaner(konkurrence):
    konkurrence2 = request.args.get('konkurrence')
    baner = Baner.query.filter(Baner.kokurrence_id == int(konkurrence)).all()

    bane_liste = []
    for i, text in enumerate(baner):
        bearbejdet = {}
        bearbejdet[text.banenavn] = text.id
        bane_liste.append(bearbejdet)

    manu_bearb = [(i.banenavn, i.id) for i in baner]
    manu_bearb = jsonify(manu_bearb)
    baneliste = jsonify(bane_liste)
    return manu_bearb

@bp.route('/get_baner/')
def _get_baner():
    loeb = request.args.get('loeb' )
    baner = [(row.id, row.banenavn) for row in Baner.query.filter_by(kokurrence_id=int(loeb)).all()]
    return jsonify(baner)

@bp.route('/_get_XMLOtrack/', methods=['GET', 'POST'])
def _get_XMLOtrack():
    konkurrence3 = request.args.get('konkurrence')
    #konkurrence4 = konkurrence_data.query.filter(konkurrence_data.id==int(konkurrence3)).first()
    #konkurrence3 = konkurrence4.otracklink
    return jsonify(konkurrence3)

@bp.route('/test_resultat/', methods=['GET', 'POST'])
def test_resultat():
    form = opload_resultat()
    start_coords = (56.471600, 9.387841)
    #folium_map = folium.Map(location=start_coords, zoom_start=8)
    poster_loc=pd.read_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\testVirtuelResultat\\Bane2.csv')
    poster_loc['coor'] = list(zip(poster_loc.latitude, poster_loc.longitude))
    spor_loc = omdan_spor()
    m = create_map1(spor_loc,poster_loc)
    #return folium_map._repr_html_()
    return render_template('resultater/upload_resultat.html', form=form, map=m._repr_html_())
    #return render_template('resultater/upload_resultat.html', form=form) 

def create_map1(spor,poster):
    #[[56.4823463535, 9.3543324788], [56.4685664086, 9.3893127563]]
    min_lon = 9.2406334712 #west
    max_lon = 9.2728563948 #east
    min_lat = 56.4265013291 #north
    max_lat = 56.4032032384 #south
    #var imageBounds = [[56.4842893746, 9.3509591466], [56.4691528421, 9.3865768693]];
    m = folium.Map(location=[spor.latitude.mean(), spor.longitude.mean()], zoom_start=16, tiles='OpenStreetMap', width=1200, height=800)
    #kort = 'C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\testVirtuelResultat\\Canvas_2_Map.jpg'
    kort = r'C:/Users/sba/OneDrive/Dokumenter/Python40/Ny_Orientering/app/static/uploads/2022-08-03Morville/Canvas_3_Map.jpg'
    img_overlay = folium.raster_layers.ImageOverlay(image=kort, bounds=[[min_lat, min_lon], [max_lat, max_lon]])
    img_overlay.add_to(m)
    #folium.LayerControl().add_to(m)
    #poster_loc=pd.read_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\Bane2.csv')
    #poster_loc['coor'] = list(zip(poster_loc.latitude, poster_loc.longitude))
    for _, row in poster.iterrows():
        if row['status'] == 'OK':
            statuscolor='green',
        else:
            statuscolor='red',

        folium.CircleMarker(
            location= [row['latitude'],row['longitude']],
            radius=10,
            #popup= row[['Condition','Location']],
                color=statuscolor,
                fill=True,
                fill_color=statuscolor
            ).add_to(m)
    with open('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\testVirtuelResultat\\MapRun_Bane_2_Undallslund_uge_25_i_2022_PXAC.csv', 'r') as csv_file:
        route_df = pd.read_csv(csv_file)

    coordinates = [tuple(x) for x in route_df[['latitude', 'longitude']].to_numpy()]
    folium.PolyLine(coordinates, weight=5).add_to(m)
    #m.add_children(plugins.ImageOverlay(kort, opacity=0.8, bounds =[[min_lat, min_lon], [max_lat, max_lon]]))
    return m

def omdan_spor():
    with open('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\testVirtuelResultat\\Bane_2_Undallslund_uge_25.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    route_info = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                #d = datetime.fromisoformat(point.time[:-1]).astimezone(timezone.utc)
                d = datetime.fromisoformat(str(point.time))
                timeconv = d.strftime('%H:%M:%S')
                route_info.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'time': timeconv
                })

    route_df = pd.DataFrame(route_info)

    route_df.to_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\testVirtuelResultat\\MapRun_Bane_2_Undallslund_uge_25_i_2022_PXAC.csv', index=False)

    #cust_loc=pd.read_excel('customer_location.xlsx')
    #hotel_loc=pd.read_excel("Hotel_location.xlsx")

    spor_loc=pd.read_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\testVirtuelResultat\\MapRun_Bane_2_Undallslund_uge_25_i_2022_PXAC.csv')
    #poster_loc=pd.read_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\Bane2.csv')

    spor_loc['coor'] = list(zip(spor_loc.latitude, spor_loc.longitude))
    #poster_loc['coor'] = list(zip(poster_loc.latitude, poster_loc.longitude))

    return spor_loc

@bp.route('/_get_test_data/<loebnr>/<bane>', methods=['GET', 'POST'])
def _get_test_data(loebnr, bane):

    klasse = bane
    #if request.method == 'POST':
    konkurrencePath = db.session.query(konkurrence_data).filter_by(id=loebnr).first()
    #ny_fil_flag_strak=konkurrencePath.ny_fil_flag_strak
    #ny_fil_strak_resultat=konkurrencePath.ny_fil_falg_resultat
    konkurrenceFil = konkurrencePath.filNavn
    konkurrenceSti = konkurrencePath.pathKonkurrenceFiler
    pathFileName = os.path.join(konkurrenceSti, konkurrenceFil)
    filnavn = bane + '.json'
    pathcorrect = os.path.join(konkurrenceSti, filnavn)
    cacheFilNavn = 'res_' + bane + '.json'

    if os.path.isfile(os.path.join(konkurrenceSti, cacheFilNavn)):
        with open(os.path.join(konkurrenceSti, cacheFilNavn), "r", encoding='utf-8') as file:
            bearbejdet = jsonify(json.load(file))
    else:
        pass
        #bearbejdet = jsonify(KlarGoer(klasse, pathFileName, pathcorrect))

    return bearbejdet
    #return bearbejdet

@bp.route('/_get_strak_data/<loebnr>/<bane>', methods=['GET', 'POST'])
def _get_strak_data(loebnr, bane):
    #bane = 190
    bane_data = Baner.query.filter(Baner.kokurrence_id==int(loebnr), Baner.id==int(bane)).first()
    #OrgPost_data = json.loads(bane_data.post_gpx)
    OrgPost_data = json.loads(bane_data.post_gpx)
    #OrgPost_data1 = jsonify(bane_data.post_gpx)
    #for j, post in enumerate(OrgPost_data):
    #    pass
    postbeskrivelser = []
    for i, post in enumerate(OrgPost_data):
        if i == 0:
            pass
        else:
            if post['Postnr'] < 10:
                postbeskrivelse = str(0) + str(post['Postnr']) + '-' + str(post['Post'])
            else:
                postbeskrivelse = str(post['Postnr']) + '-' + str(post['Post'])
            postbeskrivelser.append(postbeskrivelse)
        antalposter = i
    
    test_poster = Poster.query.filter(Poster.bane_id==int(bane)).all()
    alle_deltagere = []
    x = 0
    for hverpost in test_poster:
        if x == 0:
            deltager_post = {}
            x=x+1
        if hverpost.postnr != 0:
            if hverpost.post_navn != 'Mål':
                if hverpost.status == 'OK':
                    #if hverpost.postnr < 10:
                    if x < 10:
                        deltager_post['0' + str(x) + '-' + str(OrgPost_data[x]['Post'])] = [hverpost.tid_til_sek, hverpost.tid_til_ialt_sek]
                    else:
                        deltager_post[str(x) + '-' + str(OrgPost_data[x]['Post'])] = [hverpost.tid_til_sek, hverpost.tid_til_ialt_sek]
                    x=x+1
                else:
                    #if hverpost.postnr < 10:
                    if x < 10:
                        deltager_post['0' + str(x) + '-' + str(OrgPost_data[x]['Post'])] = [0, 0]
                    else:
                        deltager_post[str(x) + '-' + str(OrgPost_data[x]['Post'])] = [0, 0]
                    x=x+1
            else:
                deltager_stam = {}
                deltager_post['00' + '-' + 'F1'] = [hverpost.tid_til_sek, hverpost.tid_til_ialt_sek]
                deltager_stam['Navn'] = hverpost.profile.navn
                if int(hverpost.baneresultat.status) == 0:
                    deltager_stam['Samlet'] = hverpost.tid_til_ialt_sek
                else:
                    deltager_stam['Samlet'] = 0
                deltager_stam.update(deltager_post)
                x=0
                alle_deltagere.append(deltager_stam)

    z = range(2)
    for k in z:
        for i, hpost in enumerate(postbeskrivelser):
            #alle_deltagere.sort(key=lambda x: (x.get(post[0]) is 0, x.get(post[0])))
            #alle_deltagere = sorted(alle_deltagere, key=lambda x: x[post][k])
            alle_deltagere = sorted(alle_deltagere, key=lambda x: x[hpost][k] if x[hpost][k] > 0 else float('inf'))
            #alle_deltagere.sort(key=lambda x: (x.get(post[k]) is 0, x.get(post[k])))
            #print(post_data1)
            for j, t in enumerate(alle_deltagere):
                test1 = hpost
                test = t[hpost][k]
                if t[hpost][k] == 0:
                    t[hpost][k] = "   -" + " " + " "
                else:
                    if t[hpost][k] >= 3600:
                        strftidtil = time.strftime("%H:%M:%S", time.gmtime(t[hpost][k]))
                    else:
                        strftidtil = time.strftime("%M:%S", time.gmtime(t[hpost][k]))
                    if j == 0:
                        t[hpost][k] = "<span style='color:#ef0000;'><b>" + str(j + 1) + "-" + strftidtil + "</b></span>"
                    elif j == 1:
                        t[hpost][k] = "<span style='color:#0b00ef;'><b>" + str(j + 1) + "-" + strftidtil + "</b></span>"
                    elif j == 2:
                        t[hpost][k] = "<span style='color: green;'><b>" + str(j + 1) + "-" + strftidtil + "</b></span>"
                    else:
                        t[hpost][k] = str(j + 1) + "-" + strftidtil
            alle_deltagere.sort(key=lambda x: (x.get(hpost[k]) == 0, x.get(hpost[k])))

    alle_deltagere = sorted(alle_deltagere, key=lambda x: (x['Samlet'] == 0, x['Samlet']))
   
    for i, t in enumerate(alle_deltagere):
        if t['Samlet'] != 0:
            if t['Samlet'] >= 3600:
                t['Samlet'] = time.strftime("%H:%M:%S", time.gmtime(t['Samlet']))
            else:
                t['Samlet'] = time.strftime("%M:%S", time.gmtime(t['Samlet']))
        else:
            t['Samlet'] = 'Diskvalificeret'
            

    for i, apost in enumerate(postbeskrivelser):
        for j, t in enumerate(alle_deltagere):
            #temp1 = t[post]
            t[apost] = (str(t[apost][0]) + "</br>" + str(t[apost][1]))
            #strak[s] = strakpost_temp_tid + "</br>" + strakpost_temp_ialt

    
    kolonner_strak = hentStrakKolonner(postbeskrivelser)
    strak_data = [kolonner_strak, alle_deltagere]
    return jsonify(strak_data)


@bp.route('/_get_resultat_data/<loebnr>/<bane>', methods=['GET', 'POST'])
def _get_resultat_data(loebnr, bane):
    #klasse = bane
    #if request.method == 'POST':
    #konkurrencePath = db.session.query(konkurrence_data).filter_by(id=loebnr).first()
    #konkurrenceFil = konkurrencePath.filNavn
    #konkurrencePath = konkurrencePath.pathKonkurrenceFiler
    #pathFileName = os.path.join(konkurrencePath, konkurrenceFil)
    #konkurrence_data1 = db.session.query(konkurrence_data).filter_by(id=loebnr).all()
    #bane_data = db.session.query(Baner).filter_by(id=int(bane), kokurrence_id=int(bane)).first()
    #post_data = db.session.query(Poster).filter_by(bane_id=int(bane), post_navn="Mål").all()
    post_data = Poster.query.filter(Poster.bane_id==int(bane), Poster.post_navn=="Mål").all()
    #post_data = post_data.query.filter(Poster.post_navn=="Mål").all()
    alle_data = []
    for e, postd in enumerate(post_data):
        postindhold = {}
        if int(postd.tid_til_ialt_sek) < 3600:
            postindhold['Tid'] = time.strftime("%M:%S", time.gmtime(int(postd.tid_til_ialt_sek)))
        else:
            postindhold['Tid'] = time.strftime("%H:%M:%S", time.gmtime(int(postd.tid_til_ialt_sek)))
        postindhold['Navn'] = postd.profile.navn
        postindhold['Klub'] = postd.profile.klub
        postindhold['Postnr'] = postd.postnr
        if int(postd.baneresultat.status) == 0:
            postindhold['Status'] = 'OK'
        else:
            postindhold['Status'] = 'ejOK'
        postindhold['tid_til'] = postd.tid_til_sek
        postindhold['tid_til_ialt'] = postd.tid_til_ialt_sek
        alle_data.append(postindhold)
    post_data1 = sorted(alle_data, key=itemgetter('tid_til_ialt'), reverse=False)
    alle_data = []
    x = 0
    for i, deltager in enumerate(post_data1):
        hverdeltager = {}
        if deltager['Status'] == 'OK':
            if x == 0:
                NedrundetVinder = math.floor((deltager['tid_til_ialt']/60))
                Nedrundet = math.floor((deltager['tid_til_ialt']/60))
            else:
                Nedrundet = math.floor((deltager['tid_til_ialt']/60))
            Point = 100 - (Nedrundet - NedrundetVinder)
            x = x + 1
        else:
            Nedrundet = math.floor((deltager['tid_til_ialt']/60))
            Point = 1

        hverdeltager["Placering"] = i + 1
        hverdeltager["Status"] = deltager['Status']
        hverdeltager['Navn'] = deltager['Navn']
        hverdeltager['Klub'] = deltager['Klub']
        hverdeltager["Tid"] = deltager['Tid']
        hverdeltager['Point'] = Point
        alle_data.append(hverdeltager)
    
    alle_data = sorted(alle_data, key=itemgetter('Point'), reverse = True)
    antal_deltagere = len(alle_data)
    x = 1
    for t in alle_data:
        if t['Point'] != 1:
            t["Placering"] = x
            x=x+1
        else:
            t['Placering'] = antal_deltagere

    kolonner_resultat = hentResKolonner()
    #kolonner_resultat = _get_GPX_postoversigt_kolonner()
        
    #kolonner = hentResKolonner()
    #resultatdata = [kolonner, alle_data]
    resultatdata = [kolonner_resultat, alle_data]
    #filnavn = bane + '.json'
    #pathcorrect = os.path.join(konkurrencePath, filnavn)
    #bearbejdet2 = KlarGoerResultat(bane, pathFileName)
    #return jsonify(bearbejdet2)
    return jsonify(resultatdata)

@bp.route('/update/', methods=['GET', 'POST'])
def update():
    dagsdato = datetime.now()
    data2 = request.get_json()
    if 'id' not in data2:
        pass
        #abort(400)
    post = Poster.query.filter(Poster.id==data2['id']).first()
    post.status = data2['Status']
    if data2['Status'] == 'OK':
        post.status_id = 1
    else:
        post.status_id = 0
    post.status_rettet = "Rettet"
    post.status_rettet_tid = dagsdato
    #db.session.add(dan_banedata)
    db.session.commit()
    return '', 204

@bp.route('/data1/<baneresultatID>', methods=['GET', 'POST'])
def data1(baneresultatID):
    query = Poster.query.filter(Poster.baneresultat_id==int(baneresultatID)).all()
    
    postdata = []
    for post in query:
        postindhold = {}
        postindhold['id'] = post.id
        postindhold['Post'] = post.post_navn
        postindhold['Status_id'] = post.status_id
        postindhold['Status'] = post.status
        postindhold['Afstand'] = str(post.distance_fra_post) + ' m.'
        postindhold['Straek'] = str(post.straek_distance) + ' m.'
        postindhold['Straektid'] = time.strftime("%M:%S", time.gmtime(post.tid_til_sek))
        if post.tid_til_ialt_sek > 3600:
            postindhold['Samlet'] = time.strftime("%H:%M:%S", time.gmtime(post.tid_til_ialt_sek))
        else:
            postindhold['Samlet'] = time.strftime("%M:%S", time.gmtime(post.tid_til_ialt_sek))
        postindhold['Distance'] = str(post.distance) + ' m.'
        postdata.append(postindhold)

    #kolonner_resultat = _get_GPX_postoversigt_kolonner()

    #resultatdata = [kolonner_resultat, postdata]

    return jsonify(postdata)

def _get_GPX_postoversigt_kolonner():
    Kolonner = []
    Placering = {}
    Post = {}
    Status = {}
    Status_id = {}
    Afstand = {}
    Straek = {}
    Straektid = {}
    Samlet = {}
    Distance = {}

    Placering['field'] = "id"
    Placering['width'] = 100
    Kolonner.append(Placering)

    Post['field'] = "Post"
    Post['width'] = 100
    Kolonner.append(Post)
    
    Status_id['field'] = "Status_id"
    Status_id['width'] = 60
    Kolonner.append(Status_id)

    Status['field'] = "Status"
    Status['width'] = 160
    Kolonner.append(Status)

    Afstand['field'] = "Afstand"
    Afstand['width'] = 160
    Kolonner.append(Afstand)

    Straek['field'] = "Straek"
    Straek['width'] = 90
    Kolonner.append(Straek)

    Straektid['field'] = "Straektid"
    Straektid['width'] = 80
    Kolonner.append(Straektid)

    Samlet['field'] = "Samlet"
    Samlet['width'] = 80
    Kolonner.append(Samlet)

    Distance['field'] = "Distance"
    Distance['width'] = 80
    Kolonner.append(Distance)

    return Kolonner

@bp.route("/hent_GPX_fil/", methods=(['GET', 'POST']))
def hent_GPX_fil():
    form = tilfojGPXfil()
    if current_user.is_authenticated:
        lober = Profile.query.filter(Profile.id==current_user.id).first()
        Navn = lober.navn
        Klub = lober.klubber.Klubnavn
    else:
        Navn = ''
        Klub = ''
    
    klubber = hent_klubber()

    if request.method == "POST":
        if form.validate_on_submit:
            loeb_id = request.form.get('loeb')            
            bane_gpx = request.form.get('baner')
            navn_gpx = request.form.get('autoComplete1')
            klub_gpx = request.form.get('klub')
            klub_navn_gpx_temp = Klubber.query.filter(Klubber.id==int(klub_gpx)).first()
            klub_navn_gpx = klub_navn_gpx_temp.Klubnavn
            findes_lober = Profile.query.filter(Profile.navn==navn_gpx).first()
            if findes_lober == None:
                nyProfil = Profile(navn=navn_gpx, klub=klub_navn_gpx, klub_id=klub_gpx)
                db.session.add(nyProfil)
                db.session.commit()
                profile_id = nyProfil.id
            else:
                profile_id = findes_lober.id
            tilmeldt = Tilmeldte.query.filter(Tilmeldte.bane_id==int(bane_gpx), Tilmeldte.navn==navn_gpx).first()
            if tilmeldt == None:
                tilmeldt_id_gpx = 0
            else:
                tilmeldt_id_gpx = tilmeldt['id']

            #klub_gpx = request.form.get('klub')
            bane_gpx_data = Baner.query.filter(Baner.id==int(bane_gpx)).first()
            bane_gpx_navn = bane_gpx_data.banenavn
            er_uploadet = baneresultat.query.filter(baneresultat.navn==navn_gpx, baneresultat.bane_id==int(bane_gpx)).first()
            lobet = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).first()
            konkurrencenavn = lobet.konkurrence + ' ' + str(lobet.konkurrenceDatoSlut)
            lobpath=str(lobet.konkurrenceDatoSlut)+str(lobet.konkurrence)
            path_til_filer=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            
            post_data = json.loads(bane_gpx_data.post_gpx)
            kort_data = json.loads(lobet.kort_koordinater)
            
            if er_uploadet:
                banedata_id = er_uploadet.id
                gemt_resultat = json.loads(er_uploadet.resultat_data)
                gemt_resultat = Poster.query.filter(Poster.baneresultat_id==er_uploadet.id).all()
                alle_poster = []
                post_gem = {}
                for post in gemt_resultat:
                    post_gem = post.to_dict()
                    alle_poster.append(post_gem)
                    
                baneresultat_spor = json.loads(er_uploadet.spor_data)

                #if baneresultat_spor == None:
                #    pass
                #else:
                #    gemt_spor_fil = baneresultat_spor

                #function_list = [baneresultat_spor, post_data, alle_poster, kort_data, bane_gpx_navn, path_til_filer]

                map = map_create(baneresultat_spor, post_data, alle_poster, kort_data, bane_gpx_navn, path_til_filer)
                #map = map_create(function_list)
                
                flash('Lobet er uploadet, viser resultatet', category='error')
                resultatdata = 'samlet'
                kontrol=0
                #return render_template("tilmelding/tilfoj_resultatfil.html", konkurrencenavn=konkurrencenavn, kontrol=kontrol, user=current_user, loeb_alle=loeb, profile_id=lober.id, baner_alle=banerEn, navn=navn_gpx, bane=bane_gpx_navn, form=form, map=map._repr_html_(), resultat = resultatdata)
                return render_template("resultater/tilfoj_resultatfil.html", banedata_id=banedata_id, konkurrencenavn=konkurrencenavn, kontrol=kontrol, navn=navn_gpx, bane=bane_gpx_navn, form=form, map=map._repr_html_(), resultat=resultatdata)
            else:
                fil_gpx = request.files.get('GPX_file')
                if fil_gpx.filename == '':
                    flash('Ingen fil valgt', category='error')
                    return render_template("resultater/tilfoj_GPXfil.html", user=current_user, loeb_alle=loeb, form=form)
                gpx = gpxpy.parse(fil_gpx)
                #fil_gpx.save(gemt_gpx_fil)
            
            #spor_filename = navn_gpx + '_spor.json'
            #gemt_spor_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, spor_filename) # bearbejdet GPX spor
            #resultat_filename = navn_gpx + '.json'
            #gemt_resultat_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, resultat_filename) # resultatet som json fil er i db baneresultat
            
            kontrolJson, spor, statusData = start_gpx(gpx, post_data, bane_gpx_navn, navn_gpx)
            
            #kontrolJson = json.dumps(kontrolJson)
            test = json.dumps(kontrolJson)
            
            dan_banedata = baneresultat(konkurrenceId=loeb_id, profile_id=profile_id, navn=navn_gpx, klub_id=int(klub_gpx), klub=klub_navn_gpx,bane=bane_gpx_navn, bane_id=bane_gpx, status=statusData, resultat_data=kontrolJson, spor_data=spor)
            #runner = baneresultat(tilmeldte_id=er_tilmeldt.id, bane=bane_f, profile_id=profil.id, loeb_id=valgt_lob)
            db.session.add(dan_banedata)
            db.session.commit()
            banedata_id = dan_banedata.id
            #map = create_map(spor, poster, kort)
            #with open(gemt_resultat_fil, 'r') as jsonResultat:
                #reader = csv.reader(poster)
                #csv_file = csv.DictReader(poster)
            #    json_file = json.load(poster)
            #poster = []
            #spor = []
            #kort = []
            spor_data = json.loads(dan_banedata.spor_data)
            #resultat_data = list(json.loads(dan_banedata.resultat_data))
            resultat_data = dan_banedata.resultat_data
            resultat_data = resultat_data[3]
            map = map_create(spor_data, post_data, resultat_data, kort_data, bane_gpx_navn, path_til_filer)
            if map:
                resultatet = resultat_data
                samlet = []
                antal = len(resultatet)
                for a, result in enumerate(resultatet):
                    resultatdict = {}
                    if a == 0:
                        resultatdict['Post'] = "Start"
                        tidSamletTil = 0
                        afstandTil = result['afstandTil']
                    elif a == antal-1:
                        resultatdict['Post'] = "Mål"
                        tidSamletTil = result['tidSamletSek']
                        afstandTil = result['afstandTil']
                    else:
                        resultatdict['Post'] = result['Post']
                        tidSamletTil = result['tidSamletSek']
                        afstandTil = result['afstandTil']
                    resultatdict['Status'] = result['Status']
                    resultatdict['Afstand fra post'] = str(round(result['Afstand_fra'], 2)) + ' m.'
                    resultatdict['Straktid'] = result['tid']
                    if result['Post'] != 'Post0':
                        resultatdict['Samlet hertil'] = result['tidSamlet']
                    if result['Status'] == 'OK':
                        resultatdict['Godkendt'] = 1
                    else:
                        resultatdict['Godkendt'] = 0
                    postnummer = a
                    samlet.append(resultatdict)
                    dan_posterdata = Poster(post_navn=resultatdict['Post'], postnr=postnummer, postkode=0, tid_til_sek=result['tidsek'], tid_til_ialt_sek=tidSamletTil,
                        distance=result['samletAfstandTil'], straek_distance=afstandTil, distance_fra_post=round(result['Afstand_fra'], 2), status_id=resultatdict['Godkendt'], status=result['Status'], tilmeldt_id=tilmeldt_id_gpx,
                            bane_id=int(bane_gpx), profile_id=profile_id, baneresultat_id=banedata_id, konkurrence_id=lobet.id, strak_spor_til=result['straek_spor'], latitude=result['latitude'], longitude=result['longitude'] )
                    db.session.add(dan_posterdata)
                db.session.commit()
                resultatdata = samlet
                
                flash('Resultatet er beregnet', category='error')
                kontrol=0
                #return render_template("tilmelding/tilfoj_resultatfil.html", konkurrencenavn=konkurrencenavn, kontrol=kontrol, user=current_user, loeb_alle=loeb, profile_id=lober.id, baner_alle=banerEn, navn=navn_gpx, bane=bane_gpx, form=form, map=map._repr_html_(), resultat = resultatdata)
                if statusData == 1:
                    return render_template("resultater/tilfoj_resultatfil.html", banedata_id=banedata_id, konkurrencenavn=konkurrencenavn, kontrol=kontrol, navn=navn_gpx, bane=bane_gpx_navn, form=form, map=map._repr_html_(), resultat=resultatdata)
                else:
                    return redirect(url_for('resultater.resultater'))

    elif request.method == "GET":
        kontrol=1
        testdata = konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoStart<=date.today()).order_by(konkurrence_data.konkurrenceDatoStart.desc()).all()
        #for lob in konkurrence_data.query.filter(konkurrence_data.konkurrenceDato<=date.today()).order_by(konkurrence_data.konkurrenceDato).all():
        loeb = {}
        for a, lob in enumerate(testdata):    
            if a == 0:
                forste = lob.id
            loeb[lob.id] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDatoSlut)
            
        banerEn = {}
        baner_alle = []
        for bane in Baner.query.filter(Baner.kokurrence_id==forste):
            banerEn[bane.id] = str(bane.banenavn)

        for bane in Baner.query.all():
            bane_en = {}
            bane_en['id'] = bane.id
            bane_en['navn'] = str(bane.banenavn)
            baner_alle.append(bane_en)

        klubber = hent_klubber()

        return render_template("resultater/tilfoj_resultatfil.html", kontrol=kontrol, klubber=klubber, klub=Klub, user=current_user, loeb_alle=loeb, baner_alle=banerEn, form=form, navn=Navn)

@bp.route("/vis_spor/", methods=(['GET', 'POST']))
def vis_spor():
    form = tilfojGPXfil()
    loeb_id = 68
    lobet = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).first()
    lobpath=str(lobet.konkurrenceDatoSlut)+str(lobet.konkurrence)
    path_til_filer=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
    alle_spor_data = baneresultat.query.filter(baneresultat.konkurrenceId == 68, baneresultat.bane_id==190).all()
    post_gpx = Baner.query.filter(Baner.id== 190).first()
    post_data = json.loads(post_gpx.post_gpx)
    alle_spor = []
    for enkelt_spor in alle_spor_data:
        spor_data =[]
        enkelt_spor = json.loads(enkelt_spor.spor_data)
        for enkelt_punkt in enkelt_spor:
            punktet = {}
            punktet['coor'] = enkelt_punkt["coor"]
            spor_data.append(punktet)
        alle_spor.append(spor_data)
    kort_data = json.loads(lobet.kort_koordinater)
    bane_gpx_data = Baner.query.filter(Baner.id==190).first()
    bane_gpx_navn = bane_gpx_data.banenavn
    
    map = map_create_flere(alle_spor, post_data, kort_data, bane_gpx_navn, path_til_filer)

    return render_template("resultater/se_spor.html", form=form, map=map._repr_html_())
