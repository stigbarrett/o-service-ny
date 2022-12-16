from email.mime import application
from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, json, send_from_directory, Response
from flask_login import UserMixin, AnonymousUserMixin, login_manager, login_required, logout_user, current_user
from sqlalchemy import desc
from app.models import Klubber, Post, User, Profile, Tilmeldte, konkurrence_data, Baner, baneresultat, Poster
from app.administration.forms import BeregnForm, klarmelde, Opret_Loeb, TilfojKort, tilfojKMZfil, retLoeb, indsend_resultat
from app import db
from app.administration import bp
from app.administration.convertpdf import add_kort2, add_billede
from app.tilmelding.helper import hent_klubber
from app.administration.resultatfil_omdan_helper import start_her
import app
#from app import tilmelding
from sqlalchemy.sql import func
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail
import os
#from . import app
from base64 import b64encode
import base64
import datetime
from datetime import datetime, date, timedelta

#from flask_breadcrumbs import Breadcrumbs, register_breadcrumb, default_breadcrumb_root
#from flask_menu import Menu, register_menu
from pathlib import Path
#from convertpdf import add_kort2, add_billede
import shutil
from app.administration.helper import bruger_opl, dan_KMZ_coor, hent_kort
#from app.tilmelding.helper import hent_kort
import zipfile
import codecs


def unzip(file, pathTemp):
    fil = os.path.join(file, pathTemp)
    filer_ud = os.path.join(file, 'files')
    if os.path.isdir(filer_ud) is not True:
        os.mkdir(os.path.join(file, "files"))
    with zipfile.ZipFile(fil, 'r') as zip:
        
        zip.extractall(file)
        
        status = 1
    return status

def checkDir(check_dir):
    test = os.path.isdir(check_dir)
    if os.path.isdir(check_dir) != True:
        #shutil.rmtree(check_dir)
        os.mkdir(check_dir)
    #else:
    #    os.mkdir(check_dir)

@bp.route("/administration/<hvad>", methods=['GET', 'POST'])
def administration(hvad):
    funktion = int(hvad)
    idag_raw = date.today()
    idag = idag_raw.strftime("%d/%m/%Y")
    klubber = hent_klubber()
    if funktion == 1:
        form = Opret_Loeb()
        if request.method == 'GET':
            return render_template("administration/administration.html", klubber=klubber, idag=idag, form=form, funktion=funktion)
        elif request.method == 'POST':
                if form.validate_on_submit:
                    #if request.form.get('form') is not None:
                    skov_f = request.form.get('skov')
                    #print(klub)
                    klub_f = request.form.get('klub')
                    dato_f = request.form.get('dato')
                    dato_obj = datetime.strptime(dato_f, '%d-%m-%Y')
                    dato_f = dato_obj.strftime('%Y-%m-%d')
                    lob_type_f = request.form.get('type')
                    klarmeldt_f = request.form.get('klarmeldt')
                    ansvarlig_f = request.form.get('ansvarlig')
                    if klarmeldt_f == "Nej":
                        klarmeldt_f = False
                    else:
                        klarmeldt_f = True
                    emit_f = request.form.get('emitenheder')
                    if emit_f == "Nej":
                        emit_f = False
                    else:
                        emit_f = True
                    kort_f = request.form.get('kort')
                    if kort_f == "Nej":
                        kort_f = False
                    else:
                        kort_f = True
                    andet_f = request.form.get('andet')
                    #klubId = db.session.query(Klubber).filter(Klubber.id == int(klub_f)).first()
                    nyt_lob = konkurrence_data(konkurrence=skov_f, konkurrenceDato=dato_f, ansvarligNavn = ansvarlig_f, klubber_id=int(klub_f), konkurrenceType=lob_type_f, brik=emit_f, klarmeldt=klarmeldt_f, kort_download=kort_f)
                    db.session.add(nyt_lob)
                    db.session.commit()
                    flash('Løbet gemt', category='success')
                    return render_template("administration/administration.html", klubber=klubber, idag=idag, form=form, funktion=funktion)
                    #return redirect(url_for('administration.administration', hvad=2))
    elif funktion == 2:
        form=TilfojKort()
        loeb_alle = []
        loeb = {}
        
        for lob in konkurrence_data.query.filter(konkurrence_data.konkurrenceDato>=date.today()).order_by(konkurrence_data.konkurrenceDato).all():
            loeb[lob.id] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDato)
            loebPath = str(lob.konkurrenceDato)+str(lob.konkurrence)
            filnavn = "kortOplysninger.json"
            loboplysningerPath = lob.pathKonkurrenceFiler
            #loboplysningerPath = loboplysningerPath.replace("\\", "/")
            loeb_alle.append(loeb)
            #with bp.open_resource('static/' + loboplysningerPath +'/' + filnavn) as ff:
            #    loebdata = json.load(ff)
            abenfil = os.path.join(current_app.config['UPLOAD_FOLDER'], loebPath, filnavn)
            with open(abenfil, encoding='utf-8') as f:
                loebdata = json.load(f)
                print(loebdata)

        
        if request.method == "POST":
            if form.validate_on_submit:
                bane_f = request.form.get('bane')
                beskrivelse_f = request.form.get('beskrivelse')
                loeb_id = request.form.get('loeb')            
                fil_pdf = request.files.get('file')
                #fil_kmz = request.files.get('kmz_file')
                if fil_pdf.filename == '':
                    flash('Ingen fil valgt', category='error')
                    return render_template("administration/tilfoj_kort.html", user=current_user, loeb_alle=loeb, form=form)
                lobet = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).first()
                lobpath = lobet.pathKonkurrenceFiler
                #lobpath=str(lobet.konkurrenceDato)+str(lobet.konkurrence)
                path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
                #checkDir(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
                checkDir(path_til_fil)
                #fil_kmz = request.files.get('kmz_file')
                filename = fil_pdf.filename
                gemt_pdf_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
                fil_pdf.save(gemt_pdf_fil)
                #filename=fil_zip.filename
                flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
                
                if os.path.isdir(path_til_fil) is not True:
                    os.mkdir(path_til_fil)
                
                file_ext = os.path.splitext(filename)[1]
                filnavn = os.path.splitext(filename)[0]
                
                if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                    flash('Filen er ikke en PDF fil', category='error')
                    return render_template("administration/tilfoj_kort.html", user=current_user, loeb_alle=loeb, form=form)
                
                if os.path.isdir(path_til_fil) is not True:
                    os.mkdir(path_til_fil)
                
                lobet.pathKonkurrenceFiler = flask_path_til_fil

                kortJpg = add_kort2(gemt_pdf_fil, filnavn, path_til_fil)
                #kortJpg.save(os.path.join(current_app.config['UPLOAD_PATH'], lobpath, filename))
                ny_bane = Baner(kort_navn_pdf=filename, kort_navn_png=kortJpg, path_filer=flask_path_til_fil, kokurrence_id=loeb_id, bane_beskrivelse=beskrivelse_f, banenavn=bane_f, )
                
                db.session.add(ny_bane)
                db.session.commit()
            return redirect(url_for('administration.tilfoj_kort'))

        elif request.method == "GET":
            beskrivelse = ""
            return render_template("administration/administration.html", klubber=klubber, user=current_user, funktion=funktion, loeb_alle=loeb, form=form)
    elif funktion == 3:
        form = tilfojKMZfil()
        if request.method == "POST":
        #if request.form['submit_1'] == 'tilmeld':
            if form.validate_on_submit:
                #bane_f = request.form.get('bane')
                navn_f = request.form.get('skov')
                dato_f = request.form.get('dato')
                klub_f = request.form.get('klub')
                dato_obj = datetime.strptime(dato_f, '%d-%m-%Y')
                dato_f = dato_obj.strftime('%Y-%m-%d')
                
                fil_kmz = request.files.get('file')
                #fil_kmz2 = form.file.data
                
                if fil_kmz.filename == '':
                    flash('Ingen fil valgt', category='error')
                    return render_template("administration/administration.html", user=current_user, form=form)
                #lobet = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).first()
                lobpath=str(dato_f)+str(navn_f)
                path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
                flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
                #checkDir(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
                checkDir(path_til_fil)
                #fil_kmz = request.files.get('kmz_file')
                filename = fil_kmz.filename
                gemt_kmz_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
                fil_kmz.save(gemt_kmz_fil)
                kortoplysninger = unzip(path_til_fil, filename)
                status1 = dan_KMZ_coor(path_til_fil, filename)
                if status1 == 11:
                    pass

                flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
                #!!! NYT !!!
                
                nyt_lob = konkurrence_data(konkurrence=navn_f, konkurrenceDato=dato_f, klubber_id=int(klub_f), pathKonkurrenceFiler=path_til_fil)
                db.session.add(nyt_lob)
                db.session.commit()
                
                samlet = []
                for bane in status1['kort']:
                    
                    a_zip = zip(bane['baneliste'], bane['banelaengde'])
                    zipped_list = list(a_zip)
                    for banen in zipped_list:
                        baneopl={}
                        baneopl['forhold'] = bane['forhold']
                        baneopl['navn'] = banen[0]
                        baneopl['langde'] = banen[1]
                        samlet.append(baneopl)
                print(samlet)
                    
                for nyebaner in samlet:
                    banenavnet = nyebaner['navn']
                    forholdet = nyebaner['forhold']
                    laengden = nyebaner['langde']
                    nye_baner = Baner(kokurrence_id=nyt_lob.id, path_filer=path_til_fil, banenavn=banenavnet, forhold=forholdet, banelangde=int(laengden))
                    db.session.add(nye_baner)
                db.session.commit()
                if os.path.isdir(path_til_fil) is not True:
                    os.mkdir(path_til_fil)
                klub = db.session.query(Klubber).filter(Klubber.id == int(klub_f)).first()
                klub = klub.id
                form = Opret_Loeb()
                return render_template("administration/administration.html", hvad=1, funktion=1, klubber=klubber, klub=str(klub), idag=idag, form=form, skov=navn_f )
        elif request.method == "GET":
            return render_template("administration/administration.html", user=current_user, funktion=funktion, klubber=klubber, form=form)



@bp.route("/OpretLoeb/", methods=['GET', 'POST'])
@login_required
def opretlob():
    form = Opret_Loeb()
    idag_raw = date.today()
    idag = idag_raw.strftime("%d/%m/%Y")
    klubber = hent_klubber()
    #klubber = []
    #for klub in db.session.query(Klubber).all():
    #    klubber.append(klub.Klubnavn)
    if request.method == "POST":
        #if request.form['submit_1'] == 'tilmeld':
        if form.validate_on_submit:
            
            #if request.form.get('form') is not None:
            skov_f = request.form.get('skov')
            #print(klub)
            klub_f = request.form.get('klub')
            enDags_f = request.form.get('endags')
            start_dato_f = request.form.get('start_dato')
            slut_dato_f = request.form.get('slut_dato')
            if enDags_f == 'Ja':
                slut_dato_f = start_dato_f
            start_dato_obj = datetime.strptime(start_dato_f, '%d-%m-%Y')
            slut_dato_obj = datetime.strptime(slut_dato_f, '%d-%m-%Y')
            start_dato_f = start_dato_obj.strftime('%Y-%m-%d')
            slut_dato_f = slut_dato_obj.strftime('%Y-%m-%d')
            
            lob_type_f = request.form.get('type')
            klarmeldt_f = request.form.get('klarmeldt')
            ansvarlig_f = request.form.get('ansvarlig')
            fil_kmz = request.files.get('file')
            lobpath=str(slut_dato_f)+str(skov_f)
            path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
            #checkDir(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            checkDir(path_til_fil)
            #fil_kmz = request.files.get('kmz_file')
            filename = fil_kmz.filename
            gemt_kmz_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
            fil_kmz.save(gemt_kmz_fil)
            if enDags_f == "Nej":
                enDags_f = False
            else:
                enDags_f = True
            if klarmeldt_f == "Nej":
                klarmeldt_f = False
            else:
                klarmeldt_f = True
            emit_f = request.form.get('emitenheder')
            if emit_f == "Nej":
                emit_f = False
            else:
                emit_f = True
            kort_f = request.form.get('kort')
            if kort_f == "Nej":
                kort_f = False
            else:
                kort_f = True
            andet_f = request.form.get('andet')
            #klubId = db.session.query(Klubber).filter(Klubber.Klubnavn == klub_f).first()
            nyt_lob = konkurrence_data(konkurrence=skov_f, konkurrenceDatoStart=start_dato_f, enDags=enDags_f, konkurrenceDatoSlut=slut_dato_f, ansvarligNavn = ansvarlig_f, klubber_id=int(klub_f), konkurrenceType=lob_type_f, brik=emit_f, klarmeldt=klarmeldt_f, kort_download=kort_f, pathKonkurrenceFiler=path_til_fil)
            db.session.add(nyt_lob)
            db.session.commit()
            status = unzip(path_til_fil, filename)
            status1 = dan_KMZ_coor(path_til_fil, filename)
            kortoplysninger = status1['kortoplysninger']
            kontrolJson = json.loads(status1['kontrolJson'])
            kortGrundOplysninger = json.loads(status1['kortGrundOplysninger'])

            flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))

            samlet = []
            for bane in kortoplysninger['kort']:     
                a_zip = zip(bane['baneliste'], bane['banelaengde'])
                zipped_list = list(a_zip)
                for banen in zipped_list:
                    baneopl={}
                    baneopl['forhold'] = bane['forhold']
                    baneopl['navn'] = banen[0]
                    baneopl['langde'] = banen[1]
                    samlet.append(baneopl)
                
            for nyebaner in samlet:
                banenavnet = nyebaner['navn']
                forholdet = nyebaner['forhold']
                laengden = nyebaner['langde']
                nye_baner = Baner(kokurrence_id=nyt_lob.id, path_filer=flask_path_til_fil, banenavn=banenavnet, forhold=forholdet, banelangde=int(laengden))
                db.session.add(nye_baner)
            db.session.commit()

            for key, value in kontrolJson.items():
                opdater_baner = Baner.query.filter(Baner.kokurrence_id==nyt_lob.id, Baner.banenavn==key).first()
                baneOplysninger = json.dumps(value)
                opdater_baner.post_gpx = baneOplysninger
                db.session.commit()

            opdaterKonkurrence = konkurrence_data.query.filter(konkurrence_data.id==nyt_lob.id).first()
            opdaterKonkurrence.kort_koordinater = json.dumps(kortGrundOplysninger)
            db.session.commit()

            flash('Løbet gemt', category='success')
        #return redirect(url_for('administration.administration', hvad=2, form=form))
        return render_template("administration/administration.html", funktion=1, klubber=klubber, klub=klub_f, dato=slut_dato_f, idag=idag, form=form)
    
    elif request.method == "GET":
        klub_f = ''
        slut_dato_f = ''
        funktion = 1
        return render_template("administration/administration.html", user=current_user, funktion=funktion, dato=slut_dato_f, klubber=klubber, form=form)
        

@bp.route("/tilfoj_KMZfil", methods=['GET', 'POST'])
def tilfoj_KMZfil():
    form = tilfojKMZfil()
    loeb_alle = []
    loeb = {}
    
    for lob in konkurrence_data.query.filter(konkurrence_data.konkurrenceDato>=date.today()).order_by(konkurrence_data.konkurrenceDato).all():
        loeb[lob.id] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDato)
        #loeb['skov'] = lob.skov
        loeb_alle.append(loeb)

    if request.method == "POST":
        #if request.form['submit_1'] == 'tilmeld':
        if form.validate_on_submit:
            bane_f = request.form.get('bane')
            beskrivelse_f = request.form.get('beskrivelse')
            loeb_id = request.form.get('loeb')            
            #fil_zip = request.files.get('file')
            fil_kmz = request.files.get('kmz_file')
            if fil_kmz.filename == '':
                flash('Ingen fil valgt', category='error')
                return render_template("administration/tilfoj_KMZfil.html", user=current_user, loeb_alle=loeb, form=form)
            lobet = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).first()
            lobpath=str(lobet.konkurrenceDato)+str(lobet.konkurrence)
            path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            #checkDir(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            checkDir(path_til_fil)
            #fil_kmz = request.files.get('kmz_file')
            filename = fil_kmz.filename
            gemt_kmz_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
            fil_kmz.save(gemt_kmz_fil)
            #filename=fil_zip.filename
            flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
            
            if os.path.isdir(path_til_fil) is not True:
                os.mkdir(path_til_fil)
            
            #gemtfil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
            status = unzip(path_til_fil, filename)
            status1 = dan_KMZ_coor(path_til_fil, filename)
            if status1 == 11:
                pass
            
            return redirect(url_for('administration.tilfoj_KMZfil'))

    elif request.method == "GET":
        return render_template("administration/tilfoj_KMZfil.html", user=current_user, loeb_alle=loeb, form=form)

@bp.route("/tilfoj_kort", methods=['GET', 'POST'])
@login_required
def tilfoj_kort():
    funktion = 2
    form=TilfojKort(form_name='TilfojKort')
    
    loeb_alle = []
    loeb = {}
    
    #for lob in konkurrence_data.query.filter(konkurrence_data.konkurrenceDato>=date.today()).order_by(konkurrence_data.konkurrenceDato).all():
    alle_loeb = konkurrence_data.query.order_by(desc(konkurrence_data.konkurrenceDatoSlut)).all()
    for lob in alle_loeb:
        loeb = {}
        loeb['id'] = lob.id
        loeb['navn'] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDatoSlut)
        #loeb['skov'] = lob.skov
        loeb_alle.append(loeb)

    baner_alle = []
    bane_en = {}

    
    #for lob in konkurrence_data.query.filter(konkurrence_data.konkurrenceDato>=date.today()).order_by(konkurrence_data.konkurrenceDato).all():
    for bane in Baner.query.all():
        bane_en = {}
        bane_en['id'] = bane.id
        bane_en['navn'] = str(bane.banenavn)
        #loeb['skov'] = lob.skov
        baner_alle.append(bane_en)

    kortbane, kortene, kort = hent_kort(alle_loeb[0].id)
    klubber = hent_klubber()

    if request.method == "POST":
        #if request.form['submit_1'] == 'tilmeld':
        if form.validate_on_submit:
            bane_f = request.form.get('bane')
            beskrivelse_f = request.form.get('beskrivelse')
            loeb_id = request.form.get('loeb')            
            
            #fil_kmz = request.files.get('kmz_file')
            lobet = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).first()
            if int(lobet.kort_download) != 0:
                fil_pdf = request.files.get('file')
                if fil_pdf.filename == '':
                    flash('Ingen fil valgt', category='error')
                    kontrol = 1
                    return render_template("administration/_tilfojkort.html", kontrol=kontrol, user=current_user, loeb_alle=loeb, form=form)
                else:            
                    kortbane, kortene, kort = hent_kort(loeb_id)
            
                    lobpath=str(lobet.konkurrenceDatoSlut)+str(lobet.konkurrence)
                    path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
                    #checkDir(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
                    checkDir(path_til_fil)
                    #fil_kmz = request.files.get('kmz_file')
                    filename = fil_pdf.filename
                    gemt_pdf_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
                    fil_pdf.save(gemt_pdf_fil)
                    #filename=fil_zip.filename
                    flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
                    
                    if os.path.isdir(path_til_fil) is not True:
                        os.mkdir(path_til_fil)
                    
                    #gemtfil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
                    #status = unzip(path_til_fil, filename)
                    #status1 = dan_coor(path_til_fil, filename)
                    
                    file_ext = os.path.splitext(filename)[1]
                    filnavn = os.path.splitext(filename)[0]
                    #for root, dirs, files in os.walk(path_til_fil):
                    #    for file in files:
                    #        if file.endswith(".pdf"):
                    #            file_ext = os.path.splitext(filename)[1]
                    #            filnavn = os.path.splitext(filename)[0]
                    #            kortJpg = add_kort2(files, filnavn, path_til_fil)
                    #            ny_bane = Baner(kort_navn_pdf=filename, kort_navn_png=kortJpg, path_filer=flask_path_til_fil, kokurrence_id=loeb_id, bane_beskrivelse=beskrivelse_f, banenavn=bane_f, )
                    #            db.session.add(ny_bane)
                    #db.session.commit()
                    if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                        flash('Filen er ikke en PDF fil', category='error')
                        return render_template("administration/administration.html", funktion=funktion, user=current_user, baner_alle=baner_alle, loeb_alle=loeb_alle, form=form)
                    
                    #testpath = (current_app.config['UPLOAD_FOLDER'])
                    #flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
                    #path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
                    if os.path.isdir(path_til_fil) is not True:
                        os.mkdir(path_til_fil)
                    
                    #gemtfil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
                    #fil_pdf.save(gemtfil)
                    lobet.pathKonkurrenceFiler = flask_path_til_fil

                    kortJpg = add_kort2(gemt_pdf_fil, filnavn, path_til_fil)
                    #kortJpg.save(os.path.join(current_app.config['UPLOAD_PATH'], lobpath, filename))
                    #lobet = konkurrence_data.query.filter(konkurrence_data.id==loeb_id).first()
                    bane = Baner.query.filter_by(id=int(bane_f)).first()
                    bane.kort_navn_pdf = filename
                    bane.kort_navn_png = kortJpg
                    bane.bane_beskrivelse = beskrivelse_f
                    #ny_bane = Baner(kort_navn_pdf=filename, kort_navn_png=kortJpg, path_filer=flask_path_til_fil, kokurrence_id=loeb_id, bane_beskrivelse=beskrivelse_f, banenavn=bane_f, )
                    
                    #db.session.add(ny_bane)
                    db.session.commit()
                    kortbane, kortene, kort = hent_kort(loeb_id)
                kontrol = 1
                return render_template("administration/administration.html", kontrol=kontrol, funktion=funktion, user=current_user, baner_alle=baner_alle, loeb_alle=loeb_alle, form=form, kort=kortene, kortbane=kortbane, erKort=kort)
                #return redirect(url_for('administration.tilfoj_kort'))
            else:
                bane = Baner.query.filter_by(id=int(bane_f)).first()
                #bane.kort_navn_pdf = filename
                #bane.kort_navn_png = kortJpg
                bane.bane_beskrivelse = beskrivelse_f
                #ny_bane = Baner(kort_navn_pdf=filename, kort_navn_png=kortJpg, path_filer=flask_path_til_fil, kokurrence_id=loeb_id, bane_beskrivelse=beskrivelse_f, banenavn=bane_f, )
                    
                #db.session.add(ny_bane)
                db.session.commit()
                kontrol = 0
                return render_template("administration/administration.html", kontrol=kontrol,funktion=funktion, user=current_user, baner_alle=baner_alle, loeb_alle=loeb_alle, form=form)
                
    elif request.method == "GET":
        if kort == True:
            kontrol = 1
            return render_template("administration/administration.html", kontrol=kontrol,funktion=funktion, klubber=klubber, user=current_user, baner_alle=baner_alle, loeb_alle=loeb_alle, form=form, kort=kortene, kortbane=kortbane, erKort=kort)
        else:
            kontrol = 1
            return render_template("administration/administration.html", kontrol=kontrol,funktion=funktion, user=current_user, klubber=klubber, baner_alle=baner_alle, loeb_alle=loeb_alle, form=form, kort=kortene, kortbane=kortbane, erKort=kort)

def ret_boolean(vardi):
    if vardi == 'Ja':
        return 1
    else:
        return 0

@bp.route('/ret_loeb/', methods=(['GET', 'POST']))
def ret_loeb():
    funktion = 3
    form = retLoeb(form_name='retLoeb')
    idag_raw = date.today()
    igaar = idag_raw - timedelta(days = 1)
    idag = idag_raw.strftime("%d/%m/%Y")
    loeb_alle = []
    loeb = {}
    klubber = hent_klubber()
    #for lob in konkurrence_data.query.filter(konkurrence_data.konkurrenceDato>=date.today()).order_by(konkurrence_data.konkurrenceDato).all():
    alle_loeb = konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoSlut>=igaar).order_by(konkurrence_data.konkurrenceDatoSlut.desc()).all()
    for lob in alle_loeb:
        loeb = {}
        loeb['id'] = lob.id
        loeb['navn'] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDatoSlut)
        #loeb['skov'] = lob.skov
        loeb_alle.append(loeb)
    
    loeb_navn = alle_loeb[0].konkurrence
    loeb_klub = alle_loeb[0].klubber_id
    loeb_type = alle_loeb[0].konkurrenceType
    loeb_ansvarlig = alle_loeb[0].ansvarligNavn
    loeb_korttilprint = int(alle_loeb[0].kort_download)
    loeb_dato = alle_loeb[0].konkurrenceDatoSlut
    loeb_dato = loeb_dato.strftime('%d-%m-%Y')
    loeb_emit = int(alle_loeb[0].brik)
    loeb_klarmeldt = int(alle_loeb[0].klarmeldt)
    if alle_loeb[0].pathKonkurrenceFiler != None:
        kortbane, kortene, kort = hent_kort(alle_loeb[0].id)
    
    if request.method == "POST":
        #if request.form['submit_1'] == 'tilmeld':
        if form.validate_on_submit:
            loeb_ID = request.form.get('loeb')
            klub = request.form.get('klub')
            dato = request.form.get('dato')
            loeb_type = request.form.get('type')
            andet = request.form.get('andet')
            ansvarlig = request.form.get('ansvarlig')
            emit_enheder = request.form.get('emitenheder')
            klarmeldt = request.form.get('klarmeldt')
            kort_selvprint = request.form.get('kort')

            rette_data = konkurrence_data.query.filter_by(id=loeb_ID).first()
            rette_data.klubber_id = int(loeb_klub)
            rette_data.konkurrenceDato = datetime.strptime(dato, '%d-%m-%Y')
            rette_data.konkurrenceType = loeb_type
            rette_data.ansvarligNavn = ansvarlig
            rette_data.klarmeldt = ret_boolean(klarmeldt) 
            rette_data.kort_download = ret_boolean(kort_selvprint)
            rette_data.brik = ret_boolean(emit_enheder)

            db.session.commit()
            return redirect(url_for('administration.ret_loeb'))


    elif request.method == "GET":
        return render_template("administration/administration.html", funktion=funktion, user=current_user, loeb_alle=loeb_alle, klubber=klubber, klub=str(loeb_klub),
        skov=loeb_navn, kort_print=loeb_korttilprint, Type=loeb_type, Ansvarlig=loeb_ansvarlig, dato=loeb_dato,
        emit=loeb_emit, klarmeldt=loeb_klarmeldt, kort=kortene, kortbane=kortbane, erKort=kort)

@bp.route('tilfoj_resultat', methods=(['GET', 'POST']))
def tilfoj_resultat():
    funktion = 4
    form = indsend_resultat(form_name='indsend_resultat')
    idag_raw = date.today()
    igaar = idag_raw - timedelta(days = 1)
    idag = idag_raw.strftime("%d/%m/%Y")
    loeb_alle = []
    loeb = {}
    alle_loeb = konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoSlut<=igaar).order_by(konkurrence_data.konkurrenceDatoSlut.desc()).all()
    for lob in alle_loeb:
        loeb = {}
        loeb['id'] = lob.id
        loeb['navn'] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDatoSlut)
        #loeb['skov'] = lob.skov
        loeb_alle.append(loeb)
    klubber = hent_klubber()
    if request.method == "POST":
        #if request.form['submit_1'] == 'tilmeld':
        if form.validate_on_submit:
            konkurrence_fm = request.form.get('loeb')
            klub_fm = request.form.get('klub')
            indberetter_fm = request.form.get('indberetter')
            type_konkurrence_fm = request.form.get('type')
            data_format_fm = request.form.get('data_format')
            otrack_fm = request.form.get('otrack')
            #resultat_fil_fm = request.form.get('file')
            resultat_fil_fm = request.files.get('file')
            if resultat_fil_fm.filename == '':
                flash('Ingen fil valgt', category='error')
                return render_template("administration/tilfoj_KMZfil.html", user=current_user, loeb_alle=loeb, form=form)
            lobet = konkurrence_data.query.filter(konkurrence_data.id==int(konkurrence_fm)).first()
            lobpath=str(lobet.konkurrenceDatoSlut)+str(lobet.konkurrence)
            path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            #checkDir(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            checkDir(path_til_fil)
            #fil_kmz = request.files.get('kmz_file')
            filename = resultat_fil_fm.filename
            gemt_dat_fil = os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath, filename)
            resultat_fil_fm.save(gemt_dat_fil)
            #filename=fil_zip.filename
            #flask_path_til_fil=(os.path.join(current_app.config['UPLOAD_FOLDER_STATIC'], lobpath))
            
            resultat = start_her(path_til_fil, filename, lobet.id)
            #baner = resultat[0]
            deltagere = resultat[0]
            for q, deltager in enumerate(deltagere):
                findes_profil = Profile.query.filter(Profile.navn==deltager['Navn']).first()
                if findes_profil != None:
                    profilId = findes_profil.id
                else:
                    profilNavn = deltager['Navn']
                    profilKlub = deltager['Klub']
                    opret_profil = Profile(navn=profilNavn, klub=profilKlub)
                    db.session.add(opret_profil)
                    db.session.commit()
                    profilId = opret_profil.id
                baneId = Baner.query.filter(Baner.banenavn==deltager['Bane'], Baner.kokurrence_id==int(konkurrence_fm)).first()
                if deltager['Status'] != 'OK':
                    status = 1
                else:
                    status = 0
                opret_baneresultat = baneresultat(navn=deltager['Navn'], profile_id=profilId, klub=deltager['Klub'], bane=deltager['Bane'], konkurrenceId=int(konkurrence_fm), bane_id=baneId.id, status=status)
                db.session.add(opret_baneresultat)
                db.session.commit()
                baneresultatId = opret_baneresultat.id
                #x=0
                #samletAntal = len(deltager['Tider']) + 2
                gammel_sekunder = 0
                    
                antal = len(deltager['Tider'])
                
                post_navn = 'Start'
                postnr = 0
                postkode = 0
                tid_til_sek = 0
                tid_til_ialt_sek = 0
                status = deltager['Status']
                status_id = deltager['Statuskode']
                bane_id = baneId.id
                profile_id = profilId
                baneresultat_id = baneresultatId
                konkurrence_id = int(konkurrence_fm)
                gammel_sekunder = 0
                deltager_post = Poster(post_navn=post_navn, postnr=postnr, postkode=postkode, tid_til_sek=tid_til_sek, tid_til_ialt_sek=tid_til_ialt_sek, baneresultat_id=baneresultat_id, status=status, status_id=status_id, bane_id=bane_id, profile_id=profile_id,konkurrence_id=konkurrence_id)
                db.session.add(deltager_post)
                #for ii in range(len(deltager['Tider'])):
                for ii, post_paseret in enumerate(deltager['bearbejdet']):
                    #tal = int(ii) + 1
                    #postnummer = str(tal)
                    post_navn = post_paseret['post_navn']
                    postnr = int(post_paseret['postnr'])
                    postkode = int(post_paseret['postkode'])
                    tid = deltager['Tider'][ii]
                    tid_til_sek = int(tid) - int(gammel_sekunder)
                    tid_til_ialt_sek = int(tid)
                    gammel_sekunder = int(tid)
                    status = post_paseret['status']
                    status_id = post_paseret['Status_id']
                    bane_id = baneId.id
                    profile_id = profilId
                    baneresultat_id = baneresultatId
                    konkurrence_id = int(konkurrence_fm)
                    deltager_post = Poster(post_navn=post_navn, postnr=postnr, postkode=postkode, tid_til_sek=tid_til_sek, tid_til_ialt_sek=tid_til_ialt_sek, baneresultat_id=baneresultat_id, status=status, status_id=status_id, bane_id=bane_id, profile_id=profile_id,konkurrence_id=konkurrence_id)
                    db.session.add(deltager_post)
                    #gammel_sekunder = tid_til_ialt_sek
                    #x=x+1
                    
                post_navn = 'Mål'
                postnr = antal + 1
                postkode = 0
                tid_til_ialt_sek = deltager['TidSek']
                #tid = deltager['Tider'][ii]
                tid_til_sek = tid_til_ialt_sek - int(gammel_sekunder)
                #tid_til_ialt_sek = int(tid)
                
                #gammel_sekunder = int(tid)
                status = deltager['Status']
                status_id = deltager['Statuskode']
                bane_id = baneId.id
                profile_id = profilId
                baneresultat_id = baneresultatId
                konkurrence_id = int(konkurrence_fm)
                    
                deltager_post = Poster(post_navn=post_navn, postnr=postnr, postkode=postkode, tid_til_sek=tid_til_sek, tid_til_ialt_sek=tid_til_ialt_sek, baneresultat_id=baneresultat_id, status=status, status_id=status_id, bane_id=bane_id, profile_id=profile_id,konkurrence_id=konkurrence_id)
                db.session.add(deltager_post)
                
                db.session.commit()

            print('stig')

        return render_template("administration/administration.html", funktion=funktion, user=current_user, klubber=klubber, loeb_alle=loeb_alle, form=form)

    elif request.method == "GET":
        return render_template("administration/administration.html", funktion=funktion, user=current_user, klubber=klubber, loeb_alle=loeb_alle, form=form)
    

@bp.route('/get_baner/')
def _get_baner():
    loeb = request.args.get('loeb' )
    baner = [(row.id, row.banenavn) for row in Baner.query.filter_by(kokurrence_id=loeb).all()]
    return jsonify(baner)

@bp.route('/get_beskeder/')
def _get_beskeder():
    bane = request.args.get('bane' )
    #loeb = request.args.get('loeb')
    #beskeder = [(row.id, row.banebeskrivelse) for row in Baner.query.filter_by(id=int(bane)).first()]
    besked = Baner.query.filter_by(id=int(bane)).first()
    beskeder = besked.bane_beskrivelse
    if beskeder == None:
        if besked.banenavn == 'Bane 4':
            svarhed = 'Mellemsvær'
        elif besked.banenavn == 'Bane 5':
            svarhed = "Let/Begynder"
        else:
            svarhed = 'Svær'
        beskeder = svarhed + " - 1:" + besked.forhold + " - " + str(besked.banelangde) + " meter"
    
    return jsonify(beskeder)


@bp.route("/klarmeld", methods=(['GET', 'POST']))
@login_required
def klarmeld():
    profilpicture = bruger_opl()
    form=klarmelde()
    if request.method == "POST":
        if form.validate_on_submit():
            if form.submit:
                loeb_id = request.form.get('loeb')
                klarmeldlob = konkurrence_data.query.filter_by(id=loeb_id).first()
                klarmeldlob.klarmeldt = True
                db.session.commit()
                loeb_alle = []
                loeb = {}
                loeb[klarmeldlob.id] = str(klarmeldlob.skov) + ' ' + str(klarmeldlob.dato)
                #loeb_alle.append(loeb)
                modtagere = Profile.query.filter_by(mails=True).all()
                alle_modtagere = []
                for modtager in modtagere:
                    alle_modtagere.append(modtager.email)
                modtagere = alle_modtagere
                loeb = None
                subject='Løbet i ' + str(klarmeldlob.skov) + ' den ' + str(klarmeldlob.dato)
                html_content='<strong>Kortene vil være klar senere</strong>'
                ersendt = sendMails(subject, html_content, modtagere)
                svar = str(klarmeldlob.skov) + ' ' + str(klarmeldlob.dato) + ' er klarmeldt og mail sendes til abonnenter' + ersendt
                flash(svar, category='succes')
    elif request.method == "GET":
        #   loeb_alle = []
        loeb = {}
        #lob = Loeb.query.filter(Loeb.dato>=date.today(), Loeb.klarmeldt == True).order_by(Loeb.dato).all()
        for lob in konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoSlutdato>=date.today(), konkurrence_data.klarmeldt == False).order_by(konkurrence_data.konkurrenceDatoSlutdato).all():
            
            loeb[lob.id] = str(lob.skov) + ' ' + str(lob.dato)
            #loeb['skov'] = lob.skov
            #loeb_alle.append(loeb)

    return render_template("klarmeld.html", form = form, profilpicture=profilpicture, user=current_user, loeb_alle=loeb)


