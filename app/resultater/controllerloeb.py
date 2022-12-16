from app import db
#from app.models import Klub, Grunddata, Konkurrence, Baner, PostBaner, deltager_strak, Deltager, Medlemmer, baneresultat, konkurrence_data
import time
from flask import jsonify
from datetime import datetime, date
from sqlalchemy import and_
from operator import itemgetter
import json

def hent_baner(loebnr):
    baner = db.session.query(Baner).filter_by(id=loebnr).all()
    #Baner.query.filter_by(konkurrence_id=loebnr)
    return baner

def hent_sensteskov(loebnr):
    Skov1 = Konkurrence.query.filter_by(id=loebnr).first_or_404()
    return Skov1

def hent_klub(klubid):
    klub1 = Klub.query.filter_by(id=klubid).first_or_404()
    return klub1

def antal_konkurrencer():
    #test3 = db.session.query(Medlemmer.id, db.func.count(Deltager.medlemmer_id)).outerjoin(Deltager, Medlemmer.id==Deltager.medlemmer_id).filter(Deltager.bane==bane).group_by(Medlemmer.navn).all()
    Antal = db.session.query(Konkurrence.id, db.func.count(Konkurrence.id)).filter(Konkurrence.resultatOK==1).all()
    Antal = Antal[0][1]
    return Antal

def antal_konkurrencerNy():
    #test3 = db.session.query(Medlemmer.id, db.func.count(Deltager.medlemmer_id)).outerjoin(Deltager, Medlemmer.id==Deltager.medlemmer_id).filter(Deltager.bane==bane).group_by(Medlemmer.navn).all()
    Antal = db.session.query(konkurrence_data.id, db.func.count(konkurrence_data.id)).filter(konkurrence_data.konkurrenceDato>= '2022-03-30', konkurrence_data.ViKaSki_point == 'Ja').all()
    Antal = Antal[0][1]
    return Antal

def hent_k():
    Konkurrencer = dict()
    Konkurrencerklar = list()
    now1 = str(date.today())
    for s, k in db.session.query(Konkurrence, Klub).filter(Konkurrence.klub_id==Klub.id).filter(Konkurrence.dato>=now1).order_by(Konkurrence.dato.asc()).all():
        Konkurrencer['Skov'] = s.skov
        Konkurrencer['Dato'] = s.dato
        Konkurrencer['Klub'] = k.langtnavn

        Konkurrencerklar.append(Konkurrencer)
        Konkurrencer = dict()

    return Konkurrencerklar

def resultater_strak_test(bane, loebnr):
    strakpost = dict()
    #deltagerklar = []
    bane = bane
    loebnr = loebnr
    #deltagerklartemp = []
    strak = dict()
    strakklar = []
    x = 1
    for d, m in db.session.query(Deltager, Medlemmer).\
        filter(Deltager.konkurrence_id==loebnr).\
        filter(Deltager.bane==bane).\
        filter(Deltager.medlemmer_id==Medlemmer.id).all():
        #deltagerklartemp = []
        deltagerID = d.id
        #deltagere.append(m.navn)
        strak['Taeller'] = str(x)
        strak['Navn'] = m.navn

        status = d.status
        statuskode = d.statuskode
        #medlem_id = d.medlemmer_id

        if statuskode == 1:
            strak['Samlet'] = d.tid
        else:
            strak['Samlet'] = str(status)

        loberdata = db.session.query(deltager_strak).filter(deltager_strak.deltager_id==deltagerID).all()

        for s in loberdata:
            strakpost = dict()
            kode = s.post_code
            postnr = s.postnr
            if postnr < 10:
                strak['0' + str(postnr) + ' - ' + str(kode) + ""] = strakpost
                #strak['0' + str(postnr) + ' - ' + str(kode) + ""] = strakpost
            else:
                strak['' + str(postnr) + ' - ' + str(kode) + ''] = strakpost
                #strak['' + str(postnr) + '  -  ' + str(kode) + ''] = strakpost
            if s.tidTil == 0:
                strakpost['tid'] = '   -'
                strakpost['tidplac'] = ""
            else:
                strakpost['tid'] = time.strftime("%M:%S", time.gmtime(s.tidTil))
                strakpost['tidplac'] = str(s.tidTilPlac)
            
            if s.tidIalt == 0:
                strakpost['ialt'] = '   -'
                strakpost['ialtplac'] = ""
            elif s.tidIalt >= 3600:
                strakpost['ialt'] = time.strftime("%H:%M:%S", time.gmtime(s.tidIalt))
                strakpost['ialtplac'] = str(s.tidIaltPlac)
                if s.tidIaltPlac == 1:
                    strakpost['samlet'] = "<span style='color:#ef0000;'><b>" + str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt)) + "</b></span"
            else:
                strakpost['ialt'] = time.strftime("%M:%S", time.gmtime(s.tidIalt))
                strakpost['ialtplac'] = str(s.tidIaltPlac)

           
        strakklar.append(strak)
        strakpost = dict()
        strak = dict()
        x += 1
    #strakklar = jsonify(strakklar)
    #testdeltagerklar = json.dumps(strakklar, ensure_ascii=False)   
    #db.session.close()
    #print (strakklar)
    return strakklar

def hentStrakKolonner(strak_bane, loebnr):
    Kolonner = []
    TempResultat = {}
    Navn = {}
    Samlet = {}
    #x = 1
    for d in db.session.query(Baner).\
        filter(Baner.konkurrence_id==loebnr).\
        filter(Baner.baneNavn==strak_bane).all():
        baneId = d.id

    #baneId = loebnr

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

    for y in db.session.query(PostBaner).\
        filter(PostBaner.baner_id==baneId).all():
        kode = y.controlNr
        if y.postNr < 10:
            postnr = "0" + str(y.postNr)
        else:
            postnr = y.postNr
        TempResultat['field'] = (str(postnr) + "-" + str(kode))
        TempResultat['width'] = 90
        TempResultat['suppressMenu'] = True
        #TempResultat['sortable'] = True
        #TempResultat['rowSpan'] = 2
        Kolonner.append(TempResultat)
        #TempResultat.update(Resultat)
        TempResultat = {}

    return jsonify(Kolonner)

def hentStrakBane_data(strak_bane, loebnr):
    bane = strak_bane
    strak = dict()
    strakklar = []
    x = 1
    for d, m in db.session.query(Deltager, Medlemmer).\
        filter(Deltager.konkurrence_id==loebnr).\
        filter(Deltager.bane==bane).\
        filter(Deltager.medlemmer_id==Medlemmer.id).all():
        #deltagerklartemp = []
        deltagerID = d.id
        #deltagere.append(m.navn)
        #strak['Taeller'] = str(x)
        strak['Navn'] = m.navn

        status = d.status
        statuskode = d.statuskode
        #medlem_id = d.medlemmer_id

        if statuskode == 1:
            strak['Samlet'] = d.tid
        else:
            strak['Samlet'] = str(status)

        loberdata = db.session.query(deltager_strak).filter(deltager_strak.deltager_id==deltagerID).all()

        for s in loberdata:
            kode = s.post_code
            postnr = s.postnr
            if s.tidTil == 0:
                #strakpost['tid'] = '   -'
                #strakpost['tidplac'] = ""
                strakpost_temp_tid = "   -" + " " + " "
            else:
                #strakpost['tid'] = time.strftime("%M:%S", time.gmtime(s.tidTil))
                #strakpost['tidplac'] = str(s.tidTilPlac)
                if s.tidTilPlac == 1:
                    strakpost_temp_tid = "<span style='color:#ef0000;'><b>" + str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil)) + "</b></span>"
                elif s.tidTilPlac == 2:
                    strakpost_temp_tid = "<span style='color:#0b00ef;'><b>" + str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil)) + "</b></span>"
                elif s.tidTilPlac == 3:
                    strakpost_temp_tid = "<span style='color: green;'><b>" + str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil)) + "</b></span>"
                else:
                    strakpost_temp_tid = str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil))
            if s.tidIalt == 0:
                #strakpost['ialt'] = '   -'
                #strakpost['ialtplac'] = ""
                strakpost_temp_ialt = "-" + " " + " "
            elif s.tidIalt >= 3600:
                #strakpost['ialt'] = time.strftime("%H:%M:%S", time.gmtime(s.tidIalt))
                #strakpost['ialtplac'] = str(s.tidIaltPlac)
                if s.tidIaltPlac == 1:
                    strakpost_temp_ialt = "<span style='color:#ef0000;'><b>" + str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt)) + "</b></span>"
                elif s.tidIaltPlac == 2:
                    strakpost_temp_ialt = "<span style='color:#0b00ef;'><b>" + str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt)) + "</b></span>"
                elif s.tidIaltPlac == 3:
                    strakpost_temp_ialt = "<span style='color: green;'><b>" + str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt)) + "</b></span>"
                else:
                    strakpost_temp_ialt = str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt))
            else:
                #strakpost['ialt'] = time.strftime("%M:%S", time.gmtime(s.tidIalt))
                #strakpost['ialtplac'] = str(s.tidIaltPlac)
                if s.tidIaltPlac == 1:
                    strakpost_temp_ialt = "<span style='color:#ef0000;'><b>" + str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt)) + "</b></span>"
                elif s.tidIaltPlac == 2:
                    strakpost_temp_ialt = "<span style='color:#0b00ef;'><b>" + str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt)) + "</b></span>"
                elif s.tidIaltPlac == 3:
                    strakpost_temp_ialt = "<span style='color: green;'><b>" + str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt)) + "</b></span>"
                else:
                    strakpost_temp_ialt = str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt))

            #strakpost['samlet'] = strakpost_temp_tid + "<br>" + strakpost_temp_ialt

            if postnr < 10:
                strak['0' + str(postnr) + '-' + str(kode) + ""] = strakpost_temp_tid + "</br>" + strakpost_temp_ialt
                #strak['0' + str(postnr) + ' - ' + str(kode) + ""] = strakpost
            else:
                strak[str(postnr) + '-' + str(kode) + ''] = strakpost_temp_tid + "</br>" + strakpost_temp_ialt
                #strak['' + str(postnr) + '  -  ' + str(kode) + ''] = strakpost
           
        strakklar.append(strak)
        strak = dict()
        x += 1
    
    return jsonify(strakklar)

def hentResBane_data(bane, loebnr):
    deltagerklar = []
    deltager = dict()
    for d, m in db.session.query(Deltager, Medlemmer).\
        filter(Konkurrence.id==loebnr).\
        filter(Konkurrence.id==Deltager.konkurrence_id).\
        filter(Deltager.medlemmer_id==Medlemmer.id).\
        filter(Deltager.bane==bane).all():
            deltager = dict()
            #deltager['Bane'] = d.bane
            deltager['Placering'] = str(d.placering)
            deltager['Status'] = d.status
            deltager['Navn'] = m.navn
            deltager['Tid'] = d.tid
            deltager['Point'] = str(d.point)
            deltagerklar.append(deltager)
    #deltagerklar = json.dumps(deltagerklar)
    #deltagerklar = json.loads(deltagerklar)
    return jsonify(deltagerklar)

def hentResKolonnerGL(bane, loebnr):
    Kolonner = []
    Placering = {}
    Status = {}
    Navn = {}
    Tid = {}
    Point = {}
    
    Placering['field'] = "Placering"
    #Navn['pinned'] = "left"
    #Navn['rowDrag'] = True
    Placering['width'] = 100
    #Navn['filter'] = 'agSetColumnFilter'
    #Navn['menuTabs'] = ['filterMenuTab']
    Kolonner.append(Placering)

    Status['field'] = "Status"
    #Samlet['pinned'] = "left"
    Status['width'] = 100   
    #Sum['rowSpan'] = 2
    Kolonner.append(Status)

    Navn['field'] = "Navn"
    #Samlet['pinned'] = "left"
    Navn['width'] = 160
    #Sum['rowSpan'] = 2
    Kolonner.append(Navn)

    Tid['field'] = "Tid"
    #Samlet['pinned'] = "left"
    Tid['width'] = 90
    #Sum['rowSpan'] = 2
    Kolonner.append(Tid)

    Point['field'] = "Point"
    #Samlet['pinned'] = "left"
    Point['width'] = 90
    #Sum['rowSpan'] = 2
    Kolonner.append(Point)

    return jsonify(Kolonner)

def resultater_strak(bane, loebnr):
    strakpost = dict()
    #deltagerklar = []
    bane = bane
    loebnr = loebnr
    #deltagerklartemp = []
    strak = dict()
    strakklar = []
    x = 1
    for d, m in db.session.query(Deltager, Medlemmer).\
        filter(Deltager.konkurrence_id==loebnr).\
        filter(Deltager.bane==bane).\
        filter(Deltager.medlemmer_id==Medlemmer.id).all():
        #deltagerklartemp = []
        deltagerID = d.id
        #deltagere.append(m.navn)
        strak['Taeller'] = str(x)
        strak['Navn'] = m.navn

        status = d.status
        statuskode = d.statuskode
        #medlem_id = d.medlemmer_id

        if statuskode == 1:
            strak['Samlet'] = d.tid
        else:
            strak['Samlet'] = str(status)

        loberdata = db.session.query(deltager_strak).filter(deltager_strak.deltager_id==deltagerID).all()

        for s in loberdata:
            strakpost = dict()
            kode = s.post_code
            postnr = s.postnr
            if postnr < 10:
                strak['0' + str(postnr) + ' - ' + str(kode) + ""] = strakpost
                #strak['0' + str(postnr) + ' - ' + str(kode) + ""] = strakpost
            else:
                strak['' + str(postnr) + ' - ' + str(kode) + ''] = strakpost
                #strak['' + str(postnr) + '  -  ' + str(kode) + ''] = strakpost
            if s.tidTil == 0:
                strakpost['tid'] = '   -'
                strakpost['tidplac'] = ""
                strakpost_temp_tid = "   -" + " " + " "
            else:
                strakpost['tid'] = time.strftime("%M:%S", time.gmtime(s.tidTil))
                strakpost['tidplac'] = str(s.tidTilPlac)
                if s.tidTilPlac == 1:
                    strakpost_temp_tid = "<span style='color:#ef0000;'>" + str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil)) + "</span>"
                elif s.tidTilPlac == 2:
                    strakpost_temp_tid = "<span style='color:#0b00ef;'>" + str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil)) + "</span>"
                elif s.tidTilPlac == 3:
                    strakpost_temp_tid = "<span style='color: green;'>" + str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil)) + "</span>"
                else:
                    strakpost_temp_tid = str(s.tidTilPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidTil))
            
            if s.tidIalt == 0:
                strakpost['ialt'] = '   -'
                strakpost['ialtplac'] = ""
                strakpost_temp_ialt = "   -" + " " + " "
            elif s.tidIalt >= 3600:
                strakpost['ialt'] = time.strftime("%H:%M:%S", time.gmtime(s.tidIalt))
                strakpost['ialtplac'] = str(s.tidIaltPlac)
                if s.tidIaltPlac == 1:
                    strakpost_temp_ialt = "<span style='color:#ef0000;'>" + str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt)) + "</span>"
                elif s.tidIaltPlac == 2:
                    strakpost_temp_ialt = "<span style='color:#0b00ef;'>" + str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt)) + "</span>"
                elif s.tidIaltPlac == 3:
                    strakpost_temp_ialt = "<span style='color: green;'>" + str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt)) + "</span>"
                else:
                    strakpost_temp_ialt = str(s.tidIaltPlac) + "-" + time.strftime("%H:%M:%S", time.gmtime(s.tidIalt))
            else:
                strakpost['ialt'] = time.strftime("%M:%S", time.gmtime(s.tidIalt))
                strakpost['ialtplac'] = str(s.tidIaltPlac)
                if s.tidIaltPlac == 1:
                    strakpost_temp_ialt = "<span style='color:#ef0000;'>" + str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt)) + "</span>"
                elif s.tidIaltPlac == 2:
                    strakpost_temp_ialt = "<span style='color:#0b00ef;'>" + str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt)) + "</span>"
                elif s.tidIaltPlac == 3:
                    strakpost_temp_ialt = "<span style='color: green;'>" + str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt)) + "</span>"
                else:
                    strakpost_temp_ialt = str(s.tidIaltPlac) + "-" + time.strftime("%M:%S", time.gmtime(s.tidIalt))

            strakpost['samlet'] = strakpost_temp_tid + "<br>" + strakpost_temp_ialt

           
        strakklar.append(strak)
        strakpost = dict()
        strak = dict()
        x += 1
    #strakklar = jsonify(strakklar)
    #testdeltagerklar = json.dumps(strakklar, ensure_ascii=False)   
    #db.session.close()
    #print (strakklar)
    return strakklar

def resultater(bane, loeb):
    deltagerklar = []
    deltager = dict()
    for d, m in db.session.query(Deltager, Medlemmer).\
        filter(Konkurrence.id==loeb).\
        filter(Konkurrence.id==Deltager.konkurrence_id).\
        filter(Deltager.medlemmer_id==Medlemmer.id).\
        filter(Deltager.bane==bane).all():
            deltager = dict()
            #deltager['Bane'] = d.bane
            deltager['Placering'] = str(d.placering)
            deltager['Status'] = d.status
            deltager['Navn'] = m.navn
            deltager['Tid'] = d.tid
            deltager['Point'] = str(d.point)
            deltagerklar.append(deltager)
    #deltagerklar = json.dumps(deltagerklar)
    #deltagerklar = json.loads(deltagerklar)
    return deltagerklar

def hentPointOLD(bane):
    pointklar = []
    TResultat = {}
    T2Resultat = {}
    Resultat = {}
    slut_klar = dict()
    i = 0
    p = 0
	
    alle_navne = db.session.query(Medlemmer).join(Deltager).\
        filter(Deltager.bane == bane).all()
    
    Antalloeb = antal_konkurrencer()

    for row in alle_navne:
        i = i + 1
        navn = row.navn
        deltager_data = db.session.query(Deltager).join(Medlemmer).\
            filter(and_(Medlemmer.navn == navn, Deltager.bane == bane)).all()
        Resultat["Navn"] = str(row.navn)
        #sum_point = db.session.query(Medlemmer.id, db.func.sum(Deltager.point)).join(Deltager).filter(and_(Medlemmer.navn==navn, Deltager.bane==bane)).group_by(Medlemmer.navn).all()
        sum_point = db.session.query(Medlemmer.id, db.func.sum(Deltager.point)).join(Deltager).filter(and_(Medlemmer.navn==navn, Deltager.bane==bane)).group_by(Medlemmer.navn).first()
        #Resultat['Sum'] = sum_point[0][1]
        Resultat["Sum"] = sum_point[1]

        for xx in range(Antalloeb):
            Resultat["L" + str(xx + 8)] = 0
        for ii in range(len(deltager_data)):
            indholdlist = deltager_data[ii]
            for x in range (Antalloeb):
                if indholdlist.konkurrence_id == (x + 8):
                    Resultat["L" + str(x + 8)] = indholdlist.point
            TResultat = Resultat
        Resultat = {}
        T2Resultat.update(TResultat)
        pointklar.append(TResultat)
        p = p + 1
    slut_klar["data"] = pointklar
    #with open('C:\\Users\\sba\\OneDrive\\Orientering\\O-trainingsloeb_2019\\point' + bane, 'w', encoding='utf8') as PointBaner:
    #        PointBaner.write(json.dumps(slut_klar))
    return slut_klar

def hentPointKolonner(bane):
    Kolonner = []
    TempResultat = {}
    Navn = {}
    Sum = {}
    Antalloeb = antal_konkurrencer()
    loebTextAlle = [(row.skov + '-' + str(row.dato)) for row in Konkurrence.query.filter(Konkurrence.resultatOK==1).order_by(Konkurrence.id.asc()).all()]
    
    Navn['field'] = "Navn"
    Navn['pinned'] = "left"
    #Navn['rowDrag'] = True
    Navn['width'] = 140
    #Navn['filter'] = 'agSetColumnFilter'
    Navn['menuTabs'] = ['filterMenuTab']
    #Navn['rowSpan'] = 2
    
    Kolonner.append(Navn)
    Sum['field'] = "Sum"
    Sum['pinned'] = "left"
    Sum['width'] = 75
    Sum['suppressMenu'] = True
    #Sum['rowSpan'] = 2
    Kolonner.append(Sum)
    for xx in range(Antalloeb):
        loebText = loebTextAlle[xx]
        TempResultat['field'] = ("L" + str(xx + 1))
        TempResultat['width'] = 75
        TempResultat['suppressMenu'] = True
        TempResultat['tooltipShowDelay'] = 0
        TempResultat['headerTooltip'] = loebText
        TempResultat['tooltipField'] = ("L" + str(xx + 1))

        #TempResultat['rowSpan'] = 2
        Kolonner.append(TempResultat)
        #TempResultat.update(Resultat)
        TempResultat = {}
    #Kolonner.append(Resultat)
    return jsonify(Kolonner)

def hentPoint(bane):
    pointklar = []
    temp2 = db.session.query(Medlemmer).join(Deltager).\
        filter(Deltager.bane == bane).all()
    
    #test2 = db.session.query(Deltager).outerjoin(Medlemmer, Deltager.medlemmer_id==Medlemmer.id).filter(Deltager.bane==bane).group_by(Medlemmer.id).all()
    #test3 = db.session.query(Medlemmer.id, db.func.count(Deltager.medlemmer_id)).outerjoin(Deltager, Medlemmer.id==Deltager.medlemmer_id).filter(Deltager.bane==bane).group_by(Medlemmer.navn).all()
    #test4 = db.session.query(Medlemmer.id, db.func.sum(Deltager.point)).outerjoin(Deltager, Medlemmer.id==Deltager.medlemmer_id).filter(Deltager.bane==bane).group_by(Medlemmer.navn).all()
    
    Resultat = {}
    Antalloeb = antal_konkurrencer()
    i = 0
    p = 0
    TResultat = {}
    T2Resultat = {}
    slut_klar = dict()
    alle_navne = temp2

    for row in alle_navne:
        #temptest=test1[p]
        i = i + 1
        navn = row.navn
        temp_deltager1 = db.session.query(Medlemmer).join(Deltager).\
            filter(and_(Medlemmer.navn == navn, Deltager.bane == bane)).all()
        temp_deltager = db.session.query(Deltager).join(Medlemmer).\
            filter(and_(Medlemmer.navn == navn, Deltager.bane == bane)).all()
        deltager1 = temp_deltager1[0]
        deltager0 = temp_deltager
        Resultat['Navn'] = deltager1.navn
        test44 = db.session.query(Medlemmer.id, db.func.sum(Deltager.point)).join(Deltager).filter(and_(Medlemmer.navn==navn, Deltager.bane==bane)).group_by(Medlemmer.navn).all()
        Resultat['Sum'] = test44[0][1]

        for xx in range(Antalloeb):
            Resultat["L" + str(xx + 1)] = 0

        for ii in range(len(deltager0)):
            indholdlist = deltager0[ii]
            for x in range (Antalloeb):
                if indholdlist.konkurrence_id == (x + 8):
                    Resultat["L" + str(x + 1)] = indholdlist.point
            TResultat = Resultat
        Resultat = {}
        T2Resultat.update(TResultat)
        pointklar.append(TResultat)
        
        p = p + 1
    pointklar2 = sorted(pointklar, key=itemgetter('Sum'), reverse=True)
    slut_klar["data"] = pointklar2
    #return slut_klar
    return jsonify(pointklar2)

def hent_bruger_data(id):
    slut_klar = dict()
    deltagerklar = []
    deltager = dict()
    for m, d, k in db.session.query(Medlemmer, Deltager, Konkurrence).\
        filter(Medlemmer.id==id).\
        filter(Deltager.medlemmer_id==Medlemmer.id).\
        filter(Konkurrence.id==Deltager.konkurrence_id).all():

        tid = k.dato
        tid2 = tid.strftime("%d-%m-%Y")
        deltager = dict()
        deltager['Bane'] = d.bane
        deltager['Løb'] = k.skov
        deltager['Dato'] = tid2
        deltager['Placering'] = d.placering
        deltager['Tid'] = d.tid
        deltager['Point'] = d.point
        deltager['Status'] = d.status
        deltagerklar.append(deltager)
        slut_klar["data"] = deltagerklar

    #return deltagerklar, slut_klar, Navn
    return jsonify(deltagerklar)

def hent_bruger_kolonner():
    Kolonner = []
    Placering = {}
    Status = {}
    Bane = {}
    Løb = {}
    Dato = {}
    Tid = {}
    Point = {}
    Bane['field'] = "Bane"
    #Navn['pinned'] = "left"
    #Navn['rowDrag'] = True
    Bane['width'] = 90
    Bane['rowGroup'] = True
    Bane['hide'] = True
    #Navn['filter'] = 'agSetColumnFilter'
    #Navn['menuTabs'] = ['filterMenuTab']
    Kolonner.append(Bane)

    Løb['field'] = "Løb"
    #Samlet['pinned'] = "left"
    Løb['width'] = 120  
    #Sum['rowSpan'] = 2
    Kolonner.append(Løb)

    Dato['field'] = "Dato"
    #Samlet['pinned'] = "left"
    Dato['width'] = 100
    #Sum['rowSpan'] = 2
    Kolonner.append(Dato)

    Placering['field'] = "Placering"
    #Navn['pinned'] = "left"
    #Navn['rowDrag'] = True
    Placering['width'] = 80
    #Navn['filter'] = 'agSetColumnFilter'
    #Navn['menuTabs'] = ['filterMenuTab']
    Kolonner.append(Placering)

    Tid['field'] = "Tid"
    #Samlet['pinned'] = "left"
    Tid['width'] = 90
    #Sum['rowSpan'] = 2
    Kolonner.append(Tid)

    Point['field'] = "Point"
    #Samlet['pinned'] = "left"
    Point['width'] = 90
    Point['aggFunc'] = "sum"
    #Sum['rowSpan'] = 2
    Kolonner.append(Point)

    Status['field'] = "Status"
    #Samlet['pinned'] = "left"
    Status['width'] = 100   
    #Sum['rowSpan'] = 2
    Kolonner.append(Status)

    return jsonify(Kolonner)

def hent_ny_statistik1():
    deltagerklar = []
    deltagerData = dict()

    statistik_data = db.session.query(baneresultat, db.func.count(baneresultat.konkurrenceId)).\
        group_by(baneresultat.konkurrenceId)

    for row in statistik_data:
        deltager = dict()
        deltager['Løb'] = row[0].konkurrenceId_data.konkurrence
        #deltager['Løb'] = row.konkurrence_data['konkurrence']
        deltager['Arrangør_klub'] = row[0].konkurrenceId_data.arrangerendeKlub
        deltager['Antal'] = str(row[1])
        deltagerklar.append(deltager)
    
    deltagerData['data'] = deltagerklar
    deltagerklar = sorted(deltagerklar, key=itemgetter('Antal'), reverse=True)
    return deltagerklar

def hent_statistik1():
    ''' Deltager optalt og fordelt pr. løb '''
    deltagerklar = []
    deltager = dict()
    deltagerData = dict()
    #test3 = db.session.query(Medlemmer.id, db.func.count(Deltager.medlemmer_id)).outerjoin(Deltager, Medlemmer.id==Deltager.medlemmer_id).filter(Deltager.bane==bane).group_by(Medlemmer.navn).all()

    test = db.session.query(Klub, Konkurrence, db.func.count(Deltager.medlemmer_id)).\
        filter(Klub.id==Konkurrence.klub_id).\
        filter(Konkurrence.id==Deltager.konkurrence_id).\
        group_by(Konkurrence.skov).all()

    x = 1
    for row in test:
        deltager = dict()

        #deltager['Taeller'] = x
        deltager['Løb'] = row.Konkurrence.skov
        deltager['Arrangør_klub'] = row.Klub.langtnavn
        deltager['Antal'] = str(row[2])

        deltagerklar.append(deltager)
        x += 1
    deltagerData["data"] = deltagerklar
    
    deltagerklar = sorted(deltagerklar, key=itemgetter('Antal'), reverse=True)

    return deltagerklar
    #return kolonner

def hent_ny_statistik2():
    deltagerklar = []
    #deltagerData = dict()

    statistik_data1 = db.session.query(baneresultat, db.func.count(baneresultat.klub)).filter(baneresultat.klub == baneresultat.klub).group_by(baneresultat.klub)
    
    statistik_data = db.session.query(baneresultat, db.func.count(baneresultat.klub)).\
        group_by(baneresultat.klub)

    temp_data = db.session.query(baneresultat.klub.distinct()).all()
    klub_ber = []
    for klubber in temp_data:
        if statistik_data[0][0].klub == "":
            pass
        else:
            deltager = {}
            klub_ber.append(klubber[0])
            statistik_data = db.session.query(baneresultat, db.func.count(baneresultat.klub)).\
                filter(baneresultat.klub == klubber[0]).all()
            deltager['Klub'] = statistik_data[0][0].klub
            deltager['Antal'] = statistik_data[0][1]
            deltagerklar.append(deltager)

    #for row in statistik_data:
    #    deltager = dict()

    #    deltager['Klub'] = row[0].klub
        #deltager['Løb'] = row.Konkurrence.skov
    #    deltager['Antal'] = str(row[1])
    #    deltagerklar.append(deltager)
    
    deltagerklar = sorted(deltagerklar, key=itemgetter('Antal'), reverse=True)

    return deltagerklar

def hent_statistik2():
    ''' Deltager optalt og fordelt pr. klub '''
    deltagerklar = []
    deltager = dict()
    deltagerData = dict()

    test1 = db.session.query(Klub, Medlemmer, db.func.count(Deltager.medlemmer_id)).\
        filter(Deltager.medlemmer_id==Medlemmer.id).\
        filter(Medlemmer.klub_id==Klub.id).\
        group_by(Klub.langtnavn).all()

    for row in test1:
        deltager = dict()

        deltager['Klub'] = row.Klub.langtnavn
        #deltager['Løb'] = row.Konkurrence.skov
        deltager['Antal'] = row[2]

        deltagerklar.append(deltager)
    
    deltagerklar = sorted(deltagerklar, key=itemgetter('Antal'), reverse=True)

    deltagerData["data"] = deltagerklar
    #return deltagerData
    return deltagerklar

def hent_ny_statistik3():
    deltagerklar = []

    statistik_data = db.session.query(baneresultat, db.func.count(baneresultat.bane)).\
        group_by(baneresultat.bane)
    
    for row in statistik_data:
        deltager = dict()

        deltager['Bane'] = row[0].bane
        deltager['Antal løbere'] = str(row[1])
        deltagerklar.append(deltager)
    
    deltagerklar = sorted(deltagerklar, key=itemgetter('Bane'), reverse=False)

    return deltagerklar

def hent_statistik3():
    ''' Deltager optalt og fordelt pr. bane '''
    deltagerklar = []
    deltager = dict()
    deltagerData = dict()
    
    test2 = db.session.query(Deltager, db.func.count(Deltager.bane)).\
            group_by(Deltager.bane).all()

    for row in test2:
        deltager = dict()

        deltager['Bane'] = row.Deltager.bane
        #deltager['antal'] = row.Konkurrence.skov
        deltager['Antal løbere'] = row[1]

        deltagerklar.append(deltager)

    deltagerklar = sorted(deltagerklar, key=itemgetter('Bane'), reverse=False)
    deltagerData["data"] = deltagerklar
    #return deltagerData
    return deltagerklar

def hentPointKolonnerNy(bane):
    Kolonner = []
    TempResultat = {}
    Navn = {}
    Sum = {}
    Antalloeb = antal_konkurrencerNy()
    #loebTextAlle = [(row.skov + '-' + str(row.dato)) for row in Konkurrence.query.filter(Konkurrence.resultatOK==1).order_by(Konkurrence.id.asc()).all()]
    loebTextAlle = [(row.konkurrence + '-' + str(row.konkurrenceDato)) for row in konkurrence_data.query.filter(konkurrence_data.ViKaSki_point == "Ja").order_by(konkurrence_data.konkurrenceDato.asc()).all()]

    Navn['field'] = "Navn"
    Navn['pinned'] = "left"
    #Navn['rowDrag'] = True
    Navn['width'] = 140
    #Navn['filter'] = 'agSetColumnFilter'
    Navn['menuTabs'] = ['filterMenuTab']
    #Navn['rowSpan'] = 2
    Kolonner.append(Navn)
    
    Sum['field'] = "Sum"
    Sum['pinned'] = "left"
    Sum['width'] = 75
    Sum['suppressMenu'] = True
    Sum['type'] = 'rightAligned'
    #Sum['rowSpan'] = 2
    Kolonner.append(Sum)

    for xx in range(Antalloeb):
        loebText = loebTextAlle[xx]
        TempResultat['field'] = ("L" + str(xx + 1))
        TempResultat['width'] = 75
        TempResultat['type'] = 'rightAligned'
        TempResultat['suppressMenu'] = True
        TempResultat['tooltipShowDelay'] = 0
        TempResultat['headerTooltip'] = loebText
        TempResultat['tooltipField'] = ("L" + str(xx + 1))

        #TempResultat['rowSpan'] = 2
        Kolonner.append(TempResultat)
        #TempResultat.update(Resultat)
        TempResultat = {}
    #Kolonner.append(Resultat)
    return jsonify(Kolonner)

def hentPointNyOLD(bane):
    pointklar = []
    #temp2 = db.session.query(Medlemmer).join(Deltager).\
    #    filter(Deltager.bane == bane).all()
    startdato = '2022-03-30'
    temp2 = db.session.query(baneresultat).join(konkurrence_data).\
        filter(and_(baneresultat.bane == bane, konkurrence_data.konkurrenceDato >= '2022-03-30')).order_by(baneresultat.navn).all()
    #test2 = db.session.query(Deltager).outerjoin(Medlemmer, Deltager.medlemmer_id==Medlemmer.id).filter(Deltager.bane==bane).group_by(Medlemmer.id).all()
    #test3 = db.session.query(Medlemmer.id, db.func.count(Deltager.medlemmer_id)).outerjoin(Deltager, Medlemmer.id==Deltager.medlemmer_id).filter(Deltager.bane==bane).group_by(Medlemmer.navn).all()
    #test4 = db.session.query(Medlemmer.id, db.func.sum(Deltager.point)).outerjoin(Deltager, Medlemmer.id==Deltager.medlemmer_id).filter(Deltager.bane==bane).group_by(Medlemmer.navn).all()

    Resultat = {}
    Antalloeb = antal_konkurrencerNy()
    #i = 0
    #p = 0
    TResultat = {}
    T2Resultat = {}
    slut_klar = dict()
    alle_navne = temp2
    navn = ''
    glnavn = ''
    navnendelig = {}
    konsnavn = {}
    konslob = {}
    

    for row in alle_navne:
        #temptest=test1[p]
        #i = i + 1
        navn = row.navn
        medlemId = row.medlemmer_id
        temp_deltager1 = db.session.query(baneresultat).\
            filter(and_(baneresultat.medlemmer_id == medlemId, baneresultat.bane == bane)).order_by(baneresultat.navn).all()
        #temp_deltager = db.session.query(Deltager).join(Medlemmer).\
        #    filter(and_(Medlemmer.navn == navn, Deltager.bane == bane)).all()
        afholdteloeb = db.session.query(konkurrence_data).\
            filter(konkurrence_data.konkurrenceDato >= '2022-03-30')

        afholdteloebId = []
        for lob in afholdteloeb:
            afholdteloebId.append(lob.id)

        deltager1 = temp_deltager1[0]
        #deltager0 = temp_deltager1
        Resultat['Navn'] = deltager1.navn
        #test44 = db.session.query(Medlemmer.id, db.func.sum(Deltager.point)).join(Deltager).filter(and_(Medlemmer.navn==navn, Deltager.bane==bane)).group_by(Medlemmer.navn).all()
        test44ny = db.session.query(baneresultat.id, db.func.sum(baneresultat.point)).filter(and_(baneresultat.navn == navn, baneresultat.bane==bane)).group_by(baneresultat.navn).all()
        Resultat['Sum'] = test44ny[0][1]

        for xx in range(Antalloeb):
            Resultat["L" + str(xx + 1)] = 0
        
        for nummerlob, lob in enumerate(afholdteloeb):
            if len(temp_deltager1) == 1:
                if lob.id == temp_deltager1[0].konkurrenceId:
                    Resultat["L" + str(nummerlob + 1)] = temp_deltager1[0].point
            else:
                if lob.id == temp_deltager1[nummerlob].konkurrenceId:
                    Resultat["L" + str(nummerlob + 1)] = temp_deltager1[nummerlob].point
            TResultat = Resultat
        Resultat = {}
        T2Resultat.update(TResultat)
        pointklar.append(TResultat)

        #for xx in range(Antalloeb):
        #    Resultat["L" + str(xx + 1)] = 0

        
        #for y in range(len(afholdteloebId)):
        y = 0
        for lob in afholdteloebId:
            x = 0
            for deltager in temp_deltager1:
                #if x == 0:

                if lob == deltager.konkurrenceId:
                    Resultat["L" + str(y + 1)] = deltager.point
                    break
                else:
                    Resultat["L" + str(y + 1)] = 0
                    break
                x = x + 1
            TResultat = Resultat
            y = y + 1
        Resultat = {}
        #T2Resultat.update(TResultat)
        #pointklar.append(TResultat)

        #for ii in range(len(temp_deltager1)):
        #    indholdlist = deltager0[ii]
        #    for x in rangeAntalloeb):
        #        if indholdlist.konkurrenceId == :
        #            Resultat["L" + str(x + 1)] = indholdlist.point
        #    TResultat = Resultat
        #Resultat = {}
        #T2Resultat.update(TResultat)
        #pointklar.append(TResultat)

        #p = p + 1
    pointklar = sorted(pointklar, key=itemgetter('Sum'), reverse=True)
    slut_klar["data"] = pointklar
    #return slut_klar
    return jsonify(pointklar)

def hentPointNy(bane):
    pointklar = []
    if bane != "Samlet":
        temp2 = db.session.query(Medlemmer).join(baneresultat).\
            filter(baneresultat.bane == bane).all()
    else:
        temp2 = db.session.query(Medlemmer).join(baneresultat).all()
    
    Resultat = {}
    Antalloeb = antal_konkurrencerNy()
    afholdteloeb = db.session.query(konkurrence_data).\
            filter(konkurrence_data.konkurrenceDato >= '2022-03-30', konkurrence_data.ViKaSki_point == 'Ja').all()

    #afholdteloebId = []
    
    #for lob in afholdteloeb:
    #    afholdteloebId.append(lob.id)

    #i = 0
    #p = 0
    TResultat = {}
    T2Resultat = {}
    #slut_klar = dict()
    alle_navne = temp2

    for row in alle_navne:
        #i = i + 1
        navn = row.navn
        if bane != "Samlet": 
            temp_deltager1 = db.session.query(Medlemmer).join(baneresultat).join(konkurrence_data).\
                filter(and_(Medlemmer.navn == navn, konkurrence_data.ViKaSki_point == 'Ja', baneresultat.bane == bane)).all()
            temp_deltager = db.session.query(baneresultat).join(Medlemmer).join(konkurrence_data).\
                filter(and_(Medlemmer.navn == navn, konkurrence_data.ViKaSki_point == 'Ja', baneresultat.bane == bane)).all()
            test44 = db.session.query(Medlemmer.id, db.func.sum(baneresultat.point)).join(baneresultat).join(konkurrence_data).\
                filter(and_(Medlemmer.navn == navn, konkurrence_data.ViKaSki_point == 'Ja', baneresultat.bane == bane)).group_by(Medlemmer.navn).all()
        else:
            temp_deltager1 = db.session.query(Medlemmer).join(baneresultat).join(konkurrence_data).\
                filter(and_(Medlemmer.navn == navn, konkurrence_data.ViKaSki_point == 'Ja')).all()
            temp_deltager = db.session.query(baneresultat).join(Medlemmer).join(konkurrence_data).\
                filter(and_(Medlemmer.navn == navn, konkurrence_data.ViKaSki_point == 'Ja')).all()
            test44 = db.session.query(Medlemmer.id, db.func.sum(baneresultat.point)).join(baneresultat).join(konkurrence_data).\
                filter(and_(Medlemmer.navn == navn, konkurrence_data.ViKaSki_point == 'Ja')).group_by(Medlemmer.navn).all()

        if len(test44) == 0:
            Resultat['Sum'] = 0
        else:
            Resultat['Sum'] = test44[0][1]
        
        if len(temp_deltager) != 0:
            deltager1 = temp_deltager1[0]
            deltager0 = temp_deltager
            Resultat['Navn'] = deltager1.navn

            for xx in range(Antalloeb):
                Resultat["L" + str(xx + 1)] = 0
            
            x = 0
            for nummerlob, lob in enumerate(afholdteloeb):
                if len(temp_deltager) == 1:
                    if lob.id == deltager0[0].konkurrenceId:
                        Resultat["L" + str(nummerlob + 1)] = deltager0[0].point
                else:
                    if len(deltager0) >= (x + 1):
                        if lob.id == deltager0[x].konkurrenceId:
                            Resultat["L" + str(nummerlob + 1)] = deltager0[x].point
                            x = x + 1
                        
                TResultat = Resultat
            Resultat = {}
            T2Resultat.update(TResultat)
            pointklar.append(TResultat)
    
    pointklar = sorted(pointklar, key=itemgetter('Sum'), reverse=True)
    #slut_klar["data"] = pointklar
    return jsonify(pointklar)