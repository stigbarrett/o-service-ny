from email.mime import application
from wsgiref import validate
from click import format_filename
from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, json, send_from_directory, Response, abort, session
from flask_login import UserMixin, AnonymousUserMixin, login_manager, login_required, logout_user, current_user
#from flask_wtf.csrf  import CSRFProtect
from sqlalchemy import desc
from app.models import Klubber, Post, User, Profile, Tilmeldte, baneresultat, konkurrence_data, Baner, Poster
#from app.resultater.routes import create_map
from app.tilmelding.forms import Tilmeld, Tilmeld_flere, ret_tilmelding, tilfojGPXfil, alleTilmeldte
from app import db
from app.tilmelding import bp
#from app.resultater import bp 
import app
#from app import tilmelding
from sqlalchemy.sql import func
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail
import os
import tempfile
import shutil
#from . import app
from base64 import b64encode
import base64
import datetime
from datetime import datetime
from datetime import date
#from flask_breadcrumbs import Breadcrumbs, register_breadcrumb, default_breadcrumb_root
#from flask_menu import Menu, register_menu
from pathlib import Path
#from convertpdf import add_kort2, add_billede
from app.tilmelding.helper import bruger_opl, hent_deltagerliste, hent_kort, hent_fuld_deltagerliste, hent_klubber, hent_alle_deltagerliste, hent_pdf, hent_alle_tilmeldte, hent_senst_tilmeldte, hent_alle_navne
from app.tilmelding.gpx_helper import start_gpx, create_map
import folium
from folium import plugins
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import haversine as hs
import lxml
from zipfile import ZipFile
from os import listdir
from dataclasses import dataclass
#hent_tilfojede_kort, sendMails, hent_deltagers_liste, post_picture 
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail
#from flask_dropzone import Dropzone

UPLOAD_FOLDER = 'uploads'
SENDGRID_API_KEY="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"

def checkDir(check_dir):
    #test = os.path.isdir(check_dir)
    if os.path.isdir(check_dir) != True:
        #shutil.rmtree(check_dir)
        os.mkdir(check_dir)
    #else:
    #    os.mkdir(check_dir)

@bp.route("/slet_tilmeld/", methods=['POST'])
def slet_tilmeld():
    if request.method == "POST":
        pass
    udfyldt_form = request.get_json()
    tilmeldtId_f = int(udfyldt_form['tilmeldtId'])
    loebId_f = int(udfyldt_form['loebId'])
    delt = db.session.query(Tilmeldte).filter(Tilmeldte.id==tilmeldtId_f, Tilmeldte.konkurrence_id==loebId_f).first()
    db.session.delete(delt)
    #db.session.commit()
    return('sussecs!')

@bp.route("/ret_tilmeld/", methods=['POST'])
def ret_tilmeld():
    #valgt_lob = request.form.get('loebhidden')
    udfyldt_form = request.get_json()
    brikOLD_f = udfyldt_form['brikOLD']
    baneOLD_f = udfyldt_form['baneOLD']
    navn_f = udfyldt_form['navn']
    bane_f = udfyldt_form['bane']
    brik_f = udfyldt_form['briknummer']
    telefonnummer_f = udfyldt_form['telefonnummer']
    mail_f = udfyldt_form['email']
    klub_f = udfyldt_form['klub']
    loebId_f = int(udfyldt_form['loebId'])
    profileId_f = int(udfyldt_form['tilmelderId'])
    tilmeldtId_f = int(udfyldt_form['tilmeldtId'])
    if baneOLD_f != bane_f:
        delt = db.session.query(Tilmeldte).filter(Tilmeldte.id==tilmeldtId_f, Tilmeldte.konkurrence_id==loebId_f).first()
        delt.bane = bane_f
        db.session.merge(tilm)
        db.session.commit()
        
    if brikOLD_f != brik_f:
        tilm = db.session.query(Tilmeldte).filter(Tilmeldte.id == tilmeldtId_f).first()
        tilm.brik = brik_f
        db.session.merge(tilm)
        db.session.commit()
    return "succes!"


@bp.route("/add_tilmeld1/", methods=['GET','POST'])
def add_tilmeld1():
    if current_user.is_anonymous == True:
        anonym = True
    else:
        anonym = False
    udfyldt_form = request.get_json()

    navn_f = udfyldt_form['navn']
    bane_f = udfyldt_form['bane']
    brik_f = udfyldt_form['briknummer']
    telefonnummer_f = udfyldt_form['telefonnummer']
    mail_f = udfyldt_form['email']
    klub_f = int(udfyldt_form['klub'])
    loebId_f = int(udfyldt_form['loebId'])
    profileid_f = udfyldt_form['profileid']
    tilmeld_flere_f = int(udfyldt_form['tilmeld_flere'])
    find_baneid = Baner.query.filter(Baner.kokurrence_id==loebId_f, Baner.banenavn==bane_f).first()
    bane_id = find_baneid.id

    if anonym == True and udfyldt_form['profileid'] == "":
        ny_profil = Profile(navn=navn_f, brik=brik_f, email=mail_f, klub_id=klub_f, telefonnummer=telefonnummer_f )
        db.session.add(ny_profil)
        db.session.commit()
        if udfyldt_form['tilmelderId'] == 'Falsk':
            tilmelder = 1
        else:
            tilmelder = 0
        profileid_f = ny_profil.id
        if udfyldt_form['status_profilid'] != '':
            if udfyldt_form['status_profilid'] == 'Falsk':
                tilmelder_id = profileid_f
            else:
                tilmelder_id = udfyldt_form['status_profilid']
        else:
            tilmelder_id = udfyldt_form['tilmelderId']
    
    elif anonym == True and udfyldt_form['status_profilid'] != "Falsk":
        profileid_f = int(profileid_f)
        if udfyldt_form['tilmelderId'] != 'Falsk':
            tilmelder_id = int(udfyldt_form['tilmelderId'])
        else:
            tilmelder_id = int(udfyldt_form['status_profilid'])
        #if udfyldt_form['tilmelderId'] == '':
        #    tilmelder_id = profileid_f
        #else:
        #    tilmelder_id = int(udfyldt_form['tilmelderId'])
        if tilmelder_id == profileid_f:
            #if profileid_f == tilmelder_id:
            tilmelder = 1
        else:
            tilmelder = 0
    
    if anonym == False:
        er_tilmeldt = Tilmeldte.query.filter(Tilmeldte.konkurrence_id==int(udfyldt_form['loebId']), Tilmeldte.profile_id==current_user.id).first()
        tilmelder_id = current_user.id
        if er_tilmeldt == None:
            if profileid_f == '':
                ny_profil = Profile(navn=navn_f, brik=brik_f, email=mail_f, klub_id=klub_f, telefonnummer=telefonnummer_f )
                db.session.add(ny_profil)
                db.session.commit()
                profileid_f = ny_profil.id
                tilmelder = 1
            else:
                profileid_f = current_user.id
                tilmelder = 1
        else:
            tilmelder = 0
            profileid_f = int(profileid_f)
            #profileid_f = int(udfyldt_form['profileid'])

    
    
    #    if tilmeld_flere_f == 1:
    #        if session.get('Tilmelder'):
    #            tilmelder = 0
    #            profil_tilmelder = session['Tilmelder']
    #        else:
    #            session['Tilmelder'] = profileid_f
    #            session['Antal'] = 1
    #            tilmelder = 1
    #            profil_tilmelder = profileid_f
    #    else:
    #        session.pop('Tilmelder')
    #        session.pop('Antal')
    #        tilmelder = 1
    #        profil_tilmelder = profileid_f
    #if udfyldt_form['profileid'] != '':
    #    profileid_f = int(udfyldt_form['profileid'])
    #else:
    #    profileid_f = 0
     
    #if anonym == True and profileid_f == 0:
    #    ny_profil = Profile(navn=navn_f, brik=brik_f, email=mail_f, klub_id=klub_f, telefonnummer=telefonnummer_f )
    #    db.session.add(ny_profil)
    #    db.session.commit()
    #    profileid_f = ny_profil.id
    #elif anonym == True and profileid_f > 0:
    #    if tilmeld_flere_f == 1:
    #        if session.get('Tilmelder'):
    #            tilmelder = 0
    #            profil_tilmelder = session['Tilmelder']
    #        else:
    #            session['Tilmelder'] = profileid_f
    #            session['Antal'] = 1
    #            tilmelder = 1
    #            profil_tilmelder = profileid_f
    #    else:
    #        session.pop('Tilmelder')
    #        session.pop('Antal')
    #        tilmelder = 1
    #        profil_tilmelder = profileid_f

    

    #if session.get('Antal'):
    #    session['Antal'] = session['Antal'] + 1
    
    #session.permanent = False
    
    runner = Tilmeldte(navn=navn_f, tilmelder=tilmelder, bane=bane_f, bane_id=bane_id, klub_id=klub_f, konkurrence_id=loebId_f, profile_id=profileid_f, tilmelder_id=tilmelder_id)
    db.session.add(runner)
    db.session.commit()
    
    tilbage = profileid_f
    flash('Tilmelding gemt', category='success')
    return jsonify(tilbage)

def checkDir(check_dir):
    if os.path.isdir(check_dir) == True:
        shutil.rmtree(check_dir)
        os.mkdir(check_dir)
    else:
        os.mkdir(check_dir)

@bp.route("/Tilmeld/", methods=['POST'])
#@register_breadcrumb(views, '.', 'Tilmeld')
#@register_menu(views, '.', 'Tilmeld')
#@login_required
def tilmeld1():
    #profilpicture = bruger_opl()
    form = Tilmeld
    if current_user.is_anonymous == False:
        bruger_id = current_user.id
    else:
        #bruger_id = int(request.form.get('status_profileid'))
        bruger_id = int(request.form.get('tilmelderId'))
    #profil = Profile.query.filter_by(user_id=current_user.id).first()
    #user = current_user
    #form = Tilmeld
    #test = request.form
    if request.form['submit_2'] == 'slut':
        return redirect(url_for('views.tilmeldte'))
    valgt_lob = request.form.get('loeb')
    if valgt_lob is None:
        valgt_lob = request.form.get('loebhidden')
    #navn_f = request.form.get('navn')
    lob = konkurrence_data.query.filter(konkurrence_data.id==int(valgt_lob)).all()
    lobdato = (lob[0].konkurrenceDatoSlut).strftime("%d-%m-%Y")
    lobtekst = lob[0].konkurrence + " den " + lobdato
    loeb={}
    loeb[lob[0].id] = str(lob[0].konkurrence) + ' ' + str(lob[0].konkurrenceDatoSlut)
    antallob = 1
    
    kortbane, kortene, kort = hent_kort(valgt_lob)
    klubber = hent_klubber()

    #if request.form['submit_1'] == 'tilmeld':
    #    pass

    #if request.form['submit_2'] == 'kort':
        
    bestilte_kort = Tilmeldte.query.filter(Tilmeldte.konkurrence_id==int(valgt_lob), Tilmeldte.tilmelder_id==bruger_id).all()
    bestilteKort = {}
    files = []
    path_til_filer = konkurrence_data.query.filter(konkurrence_data.id==bestilte_kort[0].konkurrence_id).first()
    path_til_filer_rigtig = os.path.join(current_app.config['UPLOAD_FOLDER'],path_til_filer.pathKonkurrenceFiler)

    with tempfile.TemporaryDirectory(dir=path_til_filer_rigtig) as nytdir:
        #pathUd = os.path.join(nytdir, 'ud')
        #checkDir(pathUd)
        
        for a, kort in enumerate(bestilte_kort):
            bestilteKort[a] = kort.bane_id
            bestilt = kort.bane_id
            kortfil = Baner.query.filter(Baner.id==kort.bane_id).first()
            os.chdir(path_til_filer_rigtig)
            #(os.path.join(current_app.config['UPLOAD_FOLDER'], lobpath))
            kortfilPath = os.path.join(current_app.config['UPLOAD_FOLDER'], kortfil.path_filer, kortfil.kort_navn_pdf)
            destination = os.path.join(path_til_filer_rigtig)
            dest = shutil.copy(kortfil.kort_navn_pdf, nytdir)
            #save_to_file = "bestilte-kort.zip"
            #save_to = os.path.join(nytdir, save_to_file)
            #save_to = os.path.join(current_app.config['UPLOAD_FOLDER'], kortfilPath)
            #kortfilEndeligPath = os.path.join(current_app.config['UPLOAD_FOLDER'], kortfilPath)
            #files.append(kortfilEndeligPath)
        zipfil = "bestilte-kort.zip"
        save_to_file = os.path.join(nytdir, zipfil)
        #save_to = os.path.join(nytdir, save_to_file)
        save_to = os.path.join(current_app.config['UPLOAD_FOLDER'], kortfilPath)
        kortfilEndeligPath = os.path.join(current_app.config['UPLOAD_FOLDER'], kortfilPath)
        #os.chdir(pathUd)
        
        #pathUd = os.path.join(nytdir, 'ud')
        #checkDir(pathUd)
        #save_to = os.path.join(nytdir, save_to_file)
        #tempud = os.path.join(nytdir, pathUd)
        for file in listdir(nytdir):
            if os.path.isfile(file):
                filepath = file
                files.append(filepath)
            elif os.path.isdir(file):
                filepath = file
                files.append(filepath)
        with ZipFile(save_to_file, 'w') as zip:
            for file in files:
                zip.write(file)
        with open(save_to_file, 'rb') as f:
            data = f.readlines()
        #os.chdir(app.root_path)

    return Response(data, headers={'Content-Type': 'application/zip', 'Content-Disposition': 'attachment; filename=%s;' % zipfil})



    if request.form['submit_1'] == 'tilmeldt':
        klub_f = request.form.get('klub')
        navn_f = request.form.get('navn')
        bane_f = request.form.get('bane')
        brik_f = request.form.get('briknummer')
        telefonnummer_f = request.form.get('telefonnummer')
        mail_f = request.form.get('email')
        kunmail_f = True
        if not profil:
            profil_user = Profile(navn=navn_f, klub_id=klub_f, brik=brik_f, telefonnummer=telefonnummer_f, email=mail_f, kunNavn = 0, user_id=current_user.id, mails=0)
            db.session.add(profil_user)
            db.session.commit()
            tilmeldt = Tilmeldte(navn=navn_f, tilmelder=1, klub_id=klub_f, brik=brik_f, telefonnummer=telefonnummer_f, email=mail_f, profile_id=profil_user.id)
            db.session.add(tilmeldt)
            db.session.commit()
            profil_tilmeldt = Tilmeldte(bane=bane_f, tilmeldte_id=tilmeldt.id, profile_id=profil_user.id, loeb_id=valgt_lob)
            db.session.add(profil_tilmeldt)
            db.session.commit()
        else:
            antal_runner = Tilmeldte.query.filter_by(profile_id=profil.id, konkurrence_id=valgt_lob).all()
            tilmeldtId = Tilmeldte.query.filter_by(profile_id=profil.id, tilmelder=True).all()
            if len(antal_runner) == 0:
                runner = Tilmeldte(id=tilmeldtId[0].id, bane=bane_f, profile_id=profil.id, loeb_id=valgt_lob)
                db.session.add(runner)
                db.session.commit()
                deltagerliste = None
                liste_tilmeldte = None
            elif len(antal_runner) >= 1:
                
                er_tilmeldt = Tilmeldte.query.filter_by(navn=navn_f, email=mail_f).first()
                
                if er_tilmeldt is None:
                    tilmeldt_runner = Tilmeldte(navn=navn_f, klub_id=klub_f, brik=brik_f,
                     telefonnummer=telefonnummer_f, email=mail_f, profile_id=profil.id)
                    db.session.add(tilmeldt_runner)
                    db.session.commit()
                    deltagerliste = hent_deltagerliste(profil.id, valgt_lob)
                else:
                    for findtilmeldt in er_tilmeldt.runners:
                        if findtilmeldt.loeb_id == int(valgt_lob):
                            flash('Løberen er allerede tilmeldt', category='error')
                            #liste_tilmeldte = hent_alle_tilmeldte()
                            liste_tilmeldte = None
                            deltagerliste = hent_deltagerliste(profil.id, valgt_lob)
                            kortbane, kortene, kort = hent_kort(valgt_lob, UPLOAD_FOLDER)
                            return render_template("tilmeld_new_test.html", form=form, liste_tilmeldte=liste_tilmeldte, valgtlob=valgt_lob, tilmelderId = profil.id, lobtekst=lobtekst,
                            user=current_user, antallob=antallob, loeb_alle=loeb,
                            navn='', email='', tlfnummer='', brik='', klub='', klubber=klubber, deltagere=deltagerliste, 
                            kort=kortene, kortbane=kortbane)
                        else:
                            runner = Tilmeldte(tilmeldte_id=er_tilmeldt.id, bane=bane_f, profile_id=profil.id, loeb_id=valgt_lob)
                            db.session.add(runner)
                            db.session.commit()
                            deltagerliste = hent_deltagerliste(profil.id, valgt_lob)
                            flash('Løberen er tilmeldt', category='succes')
                
        if kort:     
            pdffiler = hent_pdf(valgt_lob, UPLOAD_FOLDER)
            for pdffil in pdffiler:
                if pdffil["banenavn"] == bane_f:
                    pdfpath = pdffil["filen"]
                    pdf_fil = pdffil["filnavn"]
            save_to = pdfpath
            save_to_file = pdf_fil
            with open(save_to, 'rb') as f:
                    data = f.readlines()
            return Response(data, headers={'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=%s;' % save_to_file})
        
        flash('Tilmelding gemt', category='success')
        return "succes!"

@bp.route("/Tilmeld/", methods=['GET'])
@login_required
def tilmeld():
    if current_user.is_anonymous == True:
        bruger = "anonym"
    else:
        bruger = current_user.id
        currentuser_profile = Profile.query.filter(Profile.user_id==bruger).first()
        
    lob = konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoSlut>=date.today(), konkurrence_data.klarmeldt == True).order_by(konkurrence_data.konkurrenceDatoSlut).all()
    
    if len(lob) < 1:
        #loeb_id = lob[0].id
    #else:
        form = Tilmeld_flere
        loeb = {}
        antallob = 0
        loeb[0] = "Ingen løb planlagt"
        return render_template("tilmelding/tilmelding.html", form=form, user=current_user, antallob=antallob, loeb_alle=loeb)
    
    if len(lob) >= 2 and lob[0].id is None:
        form = Tilmeld_flere
        antallob = len(lob)
        valgtlob = lob[0].id
        lob = lob[0]
        loeb = {}
        lobtekst = ''
        for allelob in lob:
            loeb[allelob.id] = str(allelob.konkurrence) + ' ' + str(allelob.konkurrenceDato)
        return render_template("tilmelding/tilmelding.html", form=form, user=current_user, antallob=antallob, loeb_alle=loeb)
    
    if len(lob) == 1 or lob[0].id is not None:
        form = Tilmeld
        lob = lob[0]
        #lobvalgt = False
        #if bruger == 'anonym':
        #    profil = None
        #else:
        #    profil = Profile.query.filter_by(user_id=current_user.id).first()
        #if len(lob) == 1:
        #if lob[0].id is not None:
        #    lobvalgt = True
        #    lob = lob[0]
            #lob = konkurrence_data.query.filter(konkurrence_data.id>=int(loeb_id)).first()
        #else:
        #    lob = lob[0]
        lobvalgt = True
        antallob = 1
        valgtlob = lob.id
        if lob.enDags == False:
            lobdatoStart = (lob.konkurrenceDatoStart).strftime("%d-%m-%Y")
            lobdatoSlut = (lob.konkurrenceDatoSlut).strftime("%d-%m-%Y")
            lobtekst = lob.konkurrence + " perioden fra " + lobdatoStart + " til " + lobdatoSlut
        else:
            lobdatoStart = (lob.konkurrenceDatoStart).strftime("%d-%m-%Y")
            lobtekst = lob.konkurrence + " den " + lobdatoStart
        loeb = {}
        loeb[lob.id] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDatoStart)

        kortbane, kortene, kort = hent_kort(lob.id)
        klubber = hent_klubber()
        konkurrenceNavn = lob.konkurrence
        #deltagerliste = hent_fuld_deltagerliste(lob.id)
        #navneliste = hent_alle_navne(lob.id)

        if bruger == 'anonym':
            tilmelderId = 'Falsk'
            navn = ''
            mail = ''
            tlfnummer = ''
            brik = ''
            valgtklub = ''
            tilmeldtId = ''
            deltagerliste = ''
            profil_status = "Falsk"
            valgtklub = 'Viborg OK'
            return render_template("tilmelding/tilmelding.html", form=form, tilmelderId=tilmelderId, lobvalgt=lobvalgt,
            user=bruger, valgtlob=valgtlob, lobtekst=lobtekst, antallob=antallob, loeb_alle=loeb, navn=navn, email=mail, 
            tlfnummer=tlfnummer, brik=brik, klub=valgtklub, profil_status=profil_status, klubber=klubber, lob=konkurrenceNavn, tilmeldtId=tilmeldtId, deltagere=deltagerliste, kort=kortene, kortbane=kortbane, erKort=kort)

        else:
            profil = Profile.query.filter(Profile.user_id == current_user.id).first()
            lobet_id = lob.id
            
            if profil is not None:
                profil_tilmeldte = Tilmeldte.query.filter_by(profile_id=profil.id, konkurrence_id=lobet_id).all()
                tilmelderId = profil.id
                
                if len(profil_tilmeldte) == 0:
                    deltagerliste = []
                    navn = profil.navn
                    mail = profil.email
                    tlfnummer = profil.telefonnummer
                    brik = profil.brik
                    valgtklub = str(profil.klub_id)
                    tilmeldtId = ''
                    tilmeldt = 0
                    profil_status = current_user.id
                else:
                    deltagerliste = hent_deltagerliste(profil.id, lobet_id)
                    navn = ''
                    mail = ''
                    tlfnummer = ''
                    brik = ''
                    valgtklub = ''
                    tilmeldtId = ''
                    tilmeldt = 1
                    profil_status = current_user.id
                    
                return render_template("tilmelding/tilmelding.html", form=form, tilmelderId=tilmelderId, lobvalgt=lobvalgt,
                user=current_user, valgtlob=valgtlob, lobtekst=lobtekst, profil_status=profil_status, antallob=antallob, loeb_alle=loeb, navn=navn, email=mail, 
                tlfnummer=tlfnummer, brik=brik, klub=valgtklub, klubber=klubber, tilmeldt_status=tilmeldt, tilmeldtId=tilmeldtId, deltagere=deltagerliste, kort=kortene, kortbane=kortbane, erKort=kort)
            else:
                tilmelderId = 0
                navn = current_user.username
                mail = ''
                tlfnummer = ''
                brik = ''
                valgtklub = ''
                tilmeldtId = ''
                tilmeldt = 1
                deltagerliste = ''
                #profil_status = current_user.id
                profil_status = 'Falsk'
                valgtklub = 'Viborg OK'
                
            return render_template("tilmelding/tilmelding.html", form=form, tilmelderId=tilmelderId, lobvalgt=lobvalgt,
            user=current_user, valgtlob=valgtlob, lobtekst=lobtekst, profil_status=profil_status, antallob=antallob, loeb_alle=loeb, navn=navn, email=mail, 
            tlfnummer=tlfnummer, brik=brik, klub=valgtklub, klubber=klubber, tilmeldt_status=tilmeldt, tilmeldtId=tilmeldtId, deltagere=deltagerliste, kort=kortene, kortbane=kortbane, erKort=kort)

            
    
    form = Tilmeld    
    #return render_template("tilmelding/tilmeld_new.html", form=form, lob=lob[0].konkurrence)
    return render_template("tilmelding/tilmelding.html", form=form, lob=lob[0].konkurrence, erKort=kort)

@bp.route("/Tilmeld/", methods=['GET'])
#@register_breadcrumb(views, '.', 'Tilmeld')
#@register_menu(views, '.', 'Tilmeld')
#@login_required
def tilmeldOLD():
    #form = Tilmeld(form_name='Straktider')
    #form = Tilmeld
    #profilpicture = bruger_opl()
    #user = current_user
    if current_user.is_anonymous == True:
        bruger = "anonym"
    else:
        #bruger = User.query.filter_by(id=current_user.id).first()
        bruger = current_user.id
        forste_gang = Profile.query.filter(Profile.user_id==bruger).first()
        
    lob = konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoSlut>=date.today(), konkurrence_data.klarmeldt == True).order_by(konkurrence_data.konkurrenceDatoSlut).all()
    
    #valgt_lob = request.args
    #loeb_id = valgt_lob.get("loeb")
    if len(lob) >= 1:
        loeb_id = lob[0].id
    else:
        form = Tilmeld_flere
        loeb = {}
        antallob = 0
        loeb[0] = "Ingen løb planlagt"
        return render_template("tilmelding/tilmelding.html", form=form, user=current_user, antallob=antallob, loeb_alle=loeb)
    #if len(lob) == 0:
    #    flash('Ingen løb er klarmeldt for tilmelding', category='error')
    #    return redirect(url_for('main.explore'))
    
    if len(lob) >= 2 and loeb_id is None:
        form = Tilmeld_flere
        antallob = len(lob)
        valgtlob = lob[0].id
        loeb = {}
        lobtekst = ''
        for allelob in lob:
            loeb[allelob.id] = str(allelob.konkurrence) + ' ' + str(allelob.konkurrenceDato)
    
        #return render_template("tilmelding/tilmeld_new.html", form=form, user=current_user, antallob=antallob, loeb_alle=loeb)
        return render_template("tilmelding/tilmelding.html", form=form, user=current_user, antallob=antallob, loeb_alle=loeb)
    
    if len(lob) == 1 or loeb_id is not None:
        form = Tilmeld
        #form = Tilmeld
        lobvalgt = False
        if bruger == 'anonym':
            profil = None
        else:
            profil = Profile.query.filter_by(user_id=current_user.id).first()
        #if len(lob) == 1:
        if loeb_id is not None:
            lobvalgt = True
            lob = konkurrence_data.query.filter(konkurrence_data.id>=int(loeb_id)).first()
        else:
            lob = lob[0]
        lobvalgt = True
        antallob = 1
        valgtlob = lob.id
        if lob.enDags == False:
            lobdatoStart = (lob.konkurrenceDatoStart).strftime("%d-%m-%Y")
            lobdatoSlut = (lob.konkurrenceDatoSlut).strftime("%d-%m-%Y")
            lobtekst = lob.konkurrence + " perioden fra " + lobdatoStart + " til " + lobdatoSlut
        else:
            lobdatoStart = (lob.konkurrenceDatoStart).strftime("%d-%m-%Y")
            lobtekst = lob.konkurrence + " den " + lobdatoStart
        loeb = {}
        loeb[lob.id] = str(lob.konkurrence) + ' ' + str(lob.konkurrenceDatoStart)

        kortbane, kortene, kort = hent_kort(lob.id)
        klubber = hent_klubber()
        #navneliste = hent_alle_navne()
        #klubber = []
        #for klub in db.session.query(Klubber).all():
        #    klubber.append(klub.Klubnavn)
        konkur = lob.konkurrence

        if profil is not None:
            #tilmelderId = profil.profiles[0].id
            #tilmeldte = Tilmeldte.query.filter_by(tilmelder_id = profil.profiles[0].id).all()
            lobet_id = lob.id
            profil_tilmeldte = Tilmeldte.query.filter_by(profile_id = profil.id, konkurrence_id = lobet_id).all()
            deltagerliste = hent_deltagerliste(profil.id, lobet_id)
            tilmelderId = profil.id
            
            if len(profil_tilmeldte) == 0:
                #lobet_id = lob[0].id
                navn = profil.navn
                mail = profil.email
                tlfnummer = profil.telefonnummer
                brik = profil.brik
                valgtklub = str(profil.klub_id)
                tilmeldtId = ''
                tilmeldt = 0
                profil_status = current_user.id
                #liste_tilmeldte  = None
            else:
                navn = ''
                mail = ''
                tlfnummer = ''
                brik = ''
                valgtklub = ''
                tilmeldtId = ''
                tilmeldt = 1
                profil_status = current_user.id
                #liste_tilmeldte = hent_alle_tilmeldte(lob.id, profil.id)
                #liste_tilmeldte = ''
            #return render_template("tilmelding/tilmeld_new.html", form=form, tilmelderId=tilmelderId, lobvalgt=lobvalgt,
            #user=current_user, valgtlob=valgtlob, lobtekst=lobtekst, antallob=antallob, loeb_alle=loeb, navn=navn, email=mail, 
            #tlfnummer=tlfnummer, brik=brik, klub=valgtklub, klubber=klubber, tilmeldt_status=tilmeldt, tilmeldtId=tilmeldtId, deltagere=deltagerliste, kort=kortene, kortbane=kortbane, erKort=kort)
            return render_template("tilmelding/tilmelding.html", form=form, tilmelderId=tilmelderId, lobvalgt=lobvalgt,
            user=current_user, valgtlob=valgtlob, lobtekst=lobtekst, profil_status=profil_status, antallob=antallob, loeb_alle=loeb, navn=navn, email=mail, 
            tlfnummer=tlfnummer, brik=brik, klub=valgtklub, klubber=klubber, tilmeldt_status=tilmeldt, tilmeldtId=tilmeldtId, deltagere=deltagerliste, kort=kortene, kortbane=kortbane, erKort=kort)
        else:
            tilmelderId = ''
            navn = ''
            mail = ''
            tlfnummer = ''
            brik = ''
            valgtklub = ''
            tilmeldtId = 1
            deltagerliste = ''
            profil_status = "Falsk"
            #kortene = ''
            #kortbane = ''
            #kort = ''
            valgtklub = 'Viborg OK'
            #return render_template("tilmelding/tilmeld_new.html", form=form, tilmelderId=tilmelderId, lobvalgt=lobvalgt,
            #user=current_user, valgtlob=valgtlob, lobtekst=lobtekst, antallob=antallob, loeb_alle=loeb, navn=navn, email=mail, 
            #tlfnummer=tlfnummer, brik=brik, klub=valgtklub, klubber=klubber, lob=konkur, tilmeldtId=tilmeldtId, deltagere=deltagerliste, kort=kortene, kortbane=kortbane, erKort=kort)
            return render_template("tilmelding/tilmelding.html", form=form, tilmelderId=tilmelderId, lobvalgt=lobvalgt,
            user=bruger, valgtlob=valgtlob, lobtekst=lobtekst, antallob=antallob, loeb_alle=loeb, navn=navn, email=mail, 
            tlfnummer=tlfnummer, brik=brik, klub=valgtklub, profil_status=profil_status, klubber=klubber, lob=konkur, tilmeldtId=tilmeldtId, deltagere=deltagerliste, kort=kortene, kortbane=kortbane, erKort=kort)
    
    form = Tilmeld    
    #return render_template("tilmelding/tilmeld_new.html", form=form, lob=lob[0].konkurrence)
    return render_template("tilmelding/tilmelding.html", form=form, lob=lob[0].konkurrence, erKort=kort)

@bp.route("/ret_tilmeldte", methods=(['GET', 'POST']))
@login_required
def ret_tilmeldte():
    form = ret_tilmelding

    lob = konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoSlut>=date.today(), konkurrence_data.klarmeldt == True).order_by(konkurrence_data.konkurrenceDatoSlut).all()
    klubber = hent_klubber()
    kortbane, kortene, kort = hent_kort(lob[0].id)
    antallob = len(lob)
    loeb = {}
    lobdato = (lob[0].konkurrenceDatoSlut).strftime("%d-%m-%Y")
    lobtekst = lob[0].konkurrence + " den " + lobdato
    for allelob in lob:
        loeb[allelob.id] = str(allelob.konkurrence) + ' ' + str(allelob.konkurrenceDatoSlut)
    if len(lob) == 0:
        form = Tilmeld_flere
        loeb = {}
        antallob = 0
        loeb[0] = "Ingen løb med tilmeldte"
        return render_template("tilmelding/tilmelding.html", form=form, user=current_user, antallob=antallob, loeb_alle=loeb)
    
    if current_user.is_anonymous == True:
        user = False
        tilmelderId = 0
    else:
        user = True
        tilmelderId = db.session.query(Profile).filter(Profile.user_id==current_user.id).all()
    #profilpicture = bruger_opl()
    #lob = konkurrence_data.query.filter(konkurrence_data.konkurrenceDatoSlut>=date.today(), konkurrence_data.klarmeldt == True).order_by(konkurrence_data.konkurrenceDatoSlut).all()
    
    if user == False:
        if request.method == "GET":
            if form.validate_on_submit:
                lober_tilmeldere = Tilmeldte.query.filter(Tilmeldte.konkurrence_id==lob[0].id, Tilmeldte.tilmelder==1).all()
                tabeldata=[]
    
                data={}
                dropdowndata = {}
                for enlober in lober_tilmeldere:
                    if enlober.profile.user_id == None:
                        hverData={}
                        hverData["id"] = enlober.id
                        dropdowndata[str(enlober.profile_id)] = enlober.navn
                        hverData["Navn"] = enlober.navn
                        
                        hverData['Klub'] = enlober.klubber.Klubnavn
                        hverData['Bane'] = enlober.bane
                        hverData['Brik'] = enlober.profile.brik
                        tabeldata.append(hverData)
                    
                data['data'] = tabeldata
                #data2 = jsonify(data)
                data = tabeldata
                #dropdowndata = ''
                return render_template("tilmelding/ret_tilmelding.html", form=form, dropdowndata=dropdowndata, user=user, antallob=antallob, klubber=klubber, lobtekst=lobtekst, loeb_alle=loeb,
                    kort=kortene, kortbane=kortbane, erKort=kort)
    
    if user == True:
        if request.method == "POST":
            if form.validate_on_submit:
                lober_id = int(request.form.get("navn"))
                lober = Tilmeldte.query.filter(Tilmeldte.konkurrence_id==lob[0].id, Tilmeldte.profile_id==lober_id).first()

                lober_klub = int(request.form.get("klub"))
                lober.klub_id = int(request.form.get("klub"))
                lober_email = request.form.get("email")
                lober.profile.email = request.form.get("email")
                lober_brik = request.form.get("briknummer")
                lober.profile.brik = request.form.get("briknummer")
                lober_tlf = request.form.get("telefonnummer")
                lober.profile.telefonnummer = request.form.get("telefonnummer")
                lober_bane = request.form.get("lobbane")
                lober.bane = request.form.get("lobbane")
                loeb_bane_id = Baner.query.filter(Baner.kokurrence_id==lob[0].id, Baner.banenavn==lober_bane).first()
                loebbane_id = loeb_bane_id.id
                lober.bane_id = loebbane_id
                db.session.commit()
                
    #forste_kommende = db.session.query(konkurrence_data).filter(konkurrence_data.konkurrenceDato>=date.today(), konkurrence_data.klarmeldt == True).order_by(konkurrence_data.konkurrenceDato).first()
    #loebId = request.args.get('konkurrence')
    #tilmelderId = request.args.get('tilmelder')
    loebId = lob[0].id
    
    #deltagere = hent_deltagerliste(tilmelderId[0].id, loebId)
    deltagere = Tilmeldte.query.filter(Tilmeldte.konkurrence_id==lob[0].id, Tilmeldte.tilmelder_id==current_user.id).all()
    
    tabeldata=[]
    
    data={}
    dropdowndata = {}
    for enlober in deltagere:
        hverData={}
        hverData["id"] = enlober.id
        dropdowndata[str(enlober.profile_id)] = enlober.navn
        hverData["Navn"] = enlober.navn
        hverData['Klub'] = enlober.klubber.Klubnavn
        hverData['Bane'] = enlober.bane
        hverData['Brik'] = enlober.profile.brik
        tabeldata.append(hverData)         
    data['data'] = tabeldata
    #data2 = jsonify(data)
    data = tabeldata
    
    return render_template("tilmelding/ret_tilmelding.html", form=form, dropdowndata=dropdowndata, user=user, antallob=antallob, klubber=klubber, lobtekst=lobtekst, loeb_alle=loeb,
        kort=kortene, kortbane=kortbane, erKort=kort)


@bp.route("hent_baner/", methods=['GET', 'POST'])
def hent_baner():
    konkurrence2 = request.args.get('konkurrence')
    konkurrence3 = int(konkurrence2)
    alle_baner = {}
    test = Baner.query.filter(Baner.kokurrence_id==konkurrence3).all()
    for bane in Baner.query.filter(Baner.kokurrence_id==konkurrence3).all():
        alle_baner['id'] = bane.id
        alle_baner['navn'] = bane.banenavn
        #alle_baner.append(bane.banenavn)
    banerJson = jsonify(alle_baner)
    return banerJson

@bp.route('api/profiler')
def profiler():
    profiler = Profile.query.all()
    tabeldata = []
    for enlober in profiler:
        hverData={}
        hverData['id'] = enlober.id
        hverData['Navn'] = enlober.navn
        tabeldata.append(hverData)
    return Response(json.dumps(tabeldata), mimetype='application/json')

@bp.route('api/profildata/<profil_id>')
def profildata(profil_id):
    profilensdata = Profile.query.filter(Profile.id==int(profil_id)).first()
    profildata = []
    profilindhold = {}
    
    profilindhold['klubid'] = profilensdata.klub_id
    profilindhold['klub'] = profilensdata.klubber.Klubnavn
    profilindhold['email'] = profilensdata.email
    profilindhold['briknummer'] = profilensdata.brik
    profilindhold['telefonnummer'] = profilensdata.telefonnummer
    profilindhold['id'] = profilensdata.id
    profildata.append(profilindhold)
    return Response(json.dumps(profildata), mimetype='application/json')
    #return jsonify(returtilmeldt)

@bp.route('/api/data/<baneresultatID>')
def data(baneresultatID):
    query = Poster.query.filter(Poster.baneresultat_id==int(baneresultatID)).all()
    return {
        'data': [post.to_dict() for post in query]
    }

@bp.route('/data1/<baneresultatID>')
def data1(baneresultatID):
    query = Poster.query.filter(Poster.baneresultat_id==int(baneresultatID)).all()
    
    postdata = []
    for post in query:
        postindhold = {}
        postindhold['id'] = post.id
        postindhold['Post'] = post.post_navn
        postindhold['Status'] = post.status
        postindhold['Afstand'] = post.distance_fra_post
        postindhold['Straek'] = post.straek_distance
        postindhold['Straektid'] = post.tid_til_sek
        postindhold['Samlet'] = post.tid_til_ialt_sek
        postindhold['Distance'] = post.distance
        postdata.append(postindhold)
    
    return ""

@bp.route("/alleTilmeldte/")
def alleTilmeldte():
    form = alleTilmeldte
    testdata = konkurrence_data.query.order_by(konkurrence_data.konkurrenceDatoSlut.desc()).all()
    
    loeb = {}
    for a, lob in enumerate(testdata):    
        if a == 0:
            forste_loeb_id = lob.id
        if lob.enDags == 1:
            loeb[lob.id] = str(lob.konkurrence) + ' ' + (lob.konkurrenceDatoSlut).strftime("%d-%m-%Y")
        else:
            loeb[lob.id] = str(lob.konkurrence) + ' ' + (lob.konkurrenceDatoStart).strftime("%d-%m-%Y")  + ' til ' + (lob.konkurrenceDatoSlut).strftime("%d-%m-%Y")
    
    return render_template("tilmelding/alleTilmeldte.html", form=form, valgtlob=forste_loeb_id, lobtekst=loeb[forste_loeb_id] )

@bp.route("/get_tilmeldte_tidligste", methods=(['GET', 'POST']))
def get_tilmeldte_tidligste():
    forste_kommende = db.session.query(konkurrence_data).filter(konkurrence_data.konkurrenceDato>=date.today(), konkurrence_data.klarmeldt == True).order_by(konkurrence_data.konkurrenceDato).first()
    #ret_tilmeldte = hent_deltagerliste(forste_kommende.id)
    profilId = db.session.query(Profile).filter(Profile.user_id == current_user.id).first()
    deltagere = hent_senst_tilmeldte(profilId.id, forste_kommende.id)
    return jsonify(deltagere)

@bp.route("/get_tilmeldte/<aktivt_loeb>", methods=(['GET', 'POST']))
def get_tilmeldte(aktivt_loeb):
    alle_tilmeldte = hent_alle_tilmeldte(int(aktivt_loeb), current_user.id)
    return jsonify(alle_tilmeldte)
    #return alle_tilmeldte

@bp.route("/get_tilm_deltager", defaults={'user_id' : '0'})
@bp.route("/get_tilm_deltager/<user_id>", methods=(['GET', 'POST']))
def get_tilm_deltager(user_id):
    
    tilmeld = db.session.query(Tilmeldte).filter(Tilmeldte.profile_id==int(user_id)).first()
    returtilmeldt = []
    tilmeldtedata = {}
    
    tilmeldtedata['klubid'] = tilmeld.klub_id
    tilmeldtedata['klub'] = tilmeld.klubber.Klubnavn
    tilmeldtedata['email'] = tilmeld.profile.email
    if tilmeld.profile.brik == '':
        tilmeldtedata['briknummer'] = 0
    else:
        tilmeldtedata['briknummer'] = tilmeld.profile.brik
    tilmeldtedata['telefonnummer'] = tilmeld.profile.telefonnummer
    tilmeldtedata['tilmeldtId'] = user_id
    tilmeldtedata['lobbane'] = tilmeld.bane
    tilmeldtedata['lobbane_id'] = tilmeld.bane_id
    returtilmeldt.append(tilmeldtedata)
    return jsonify(returtilmeldt)

@bp.route("/get_alle_tilmeldte/<aktivt_loeb>", methods=(['GET', 'POST']))
def get_alle_tilmeldte(aktivt_loeb):
    # bruges til at skaffe data til autocomplete
    loebId = request.args.get('konkurrence')
    navneliste = hent_alle_navne(aktivt_loeb)
    tabeldata = []
    data = {}
    for enlober in navneliste:
        hverData={}
        hverData['id'] = enlober['id']
        hverData['Navn'] = enlober["navn"]
        #hverData['Klub'] = enlober["Klub"]
        #hverData['Bane'] = enlober["Bane"]
        #hverData['Brik'] = enlober["Brik"]
        tabeldata.append(hverData)
    data['data'] = tabeldata
    #data = tabeldata
    data2 = jsonify(tabeldata)
    return Response(json.dumps(tabeldata), mimetype='application/json')
    #return data2

@bp.route("/get_deltagere/", methods=['GET', 'POST'])
def get_deltagere():
    # bruges til at skaffe data til tabellen
    valgt_lob = request.form.get('loebhidden')
    loebId = request.args.get('konkurrence')
    tilmelderId = request.args.get('tilmelder') 
    deltagere = hent_deltagerliste(tilmelderId, loebId)
    
    tabeldata=[]
    data={}
    for enlober in deltagere:
        hverData={}
        hverData['Navn'] = enlober["Navn"]
        hverData['Klub'] = enlober["Klub"]
        hverData['Bane'] = enlober["Bane"]
        hverData['Brik'] = enlober["Brik"]
        tabeldata.append(hverData)
    data['data'] = tabeldata
    #data = tabeldata
    data2 = jsonify(data)
    return data2

@bp.route("/get_alle_deltagere", methods=['GET', 'POST'])
def get_alle_deltagere():
    # bruges til at skaffe data til tabellen
    #valgt_lob = request.form.get('loebhidden')
    loebId = request.args.get('konkurrence')
    #tilmelderId = request.args.get('tilmelder') 
    deltagere = hent_fuld_deltagerliste(loebId)
    
    tabeldata=[]
    data={}
    for enlober in deltagere:
        hverData={}
        hverData['Navn'] = enlober["Navn"]
        hverData['Klub'] = enlober["Klub"]
        hverData['Bane'] = enlober["Bane"]
        hverData['Brik'] = enlober["Brik"]
        tabeldata.append(hverData)
    data['data'] = tabeldata
    #data = tabeldata
    data2 = jsonify(data)
    return data2