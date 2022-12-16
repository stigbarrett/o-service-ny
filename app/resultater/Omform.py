import datetime
import json, codecs

def baner(indholdList, path, skov, fil_baner):
    '''Danner banedata. Bane nummer og poster på bane. Skriver fil med banens indhold'''
    #BanerKlar = dict()
    Poster = dict()
    Test = dict()
    for y in range(len(indholdList)):
        if y == 1:
            Bane = indholdList[y]
            Bane = Bane[0:6]
        elif y > 1 and y < len(indholdList) - 1:
            Postnr = "Post " + (str(y - 1))
            Poster[Postnr] = indholdList[y]
            Test[Bane] = Poster
        
        #BanerKlar.update(Test)
    #if x == 1:
    #    with open(path + skov + '\\' + fil_baner, 'a', encoding='utf8') as PostBaner:
    #        PostBaner.write(json.dumps(BanerKlar))
    #else:
    #    with open(path + skov + '\\' + fil_baner, 'a', encoding='utf8') as PostBaner:
    #        PostBaner.write(json.dumps(BanerKlar))
    return Bane, Test

def vendom(indholdList):
    navn = indholdList[3]
    opdelt = navn.split()
    efternavn = opdelt[0]
    del opdelt[0]
    seperator = ' '
    print (navn)
    if len(opdelt) >= 1:
        fornavn = seperator.join(opdelt)
    else:
        fornavn = opdelt[-1]
    nytnavn = fornavn + " " + efternavn
    return nytnavn

def SaetStatus(indholdList, Bane):
    ''' Danner status data for løber '''
    indholdList.insert(0, Bane)
    if str(indholdList[0]) == ('"X"#Diskvalificeret'):
        indholdList.insert(1, "Diskvalificeret")
        status = 3
    elif str(indholdList[0]) == ('"X"#Udgået'):
        indholdList.insert(1, "Udgaaet")
        status = 2
    elif str(indholdList[0]) == ('"X"#Ingen sluttid'):
        indholdList.insert(1, "IngenTid")
        status = 4
    elif str(indholdList[0]) == ('"X"'):
        del indholdList[0]
        indholdList.insert(1, "OK")
        status = 1
    if status != 1:
        del indholdList[2]
    
    del indholdList[2]
    indholdList.insert(2, 0)
    indholdList.insert(-1, 0)
    return status

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def omdan(loebnr, mappe, path):
    '''Variable der skal sættes for hvert løb'''
    #path = 'C:\\Users\\sba\\OneDrive\\Orientering\\O-trainingsloeb_2019\\'
    #skov = '01_FeldborgNord'
    fil_resultat = 'Resultat.dat'
    fil_baner = 'PostBaner1.json'
    fil_bearbejdet = 'Bearbejdet1.json'
    efternavn_forst = 1
    BanerKlar = []
    #path_baner = (path + mappe + '\\' + fil_baner)
    #(path + skov + '\\' + fil_baner, 'w')
    fil = (path + mappe + '\\' + fil_resultat)
    with open(fil, 'r', encoding='utf8') as f:
        indhold = f.readlines()
        Deltager = dict()
        DeltagerKlar = []
        for i in range(len(indhold)):
            indholdList = [int(e) if e.isdigit() else e for e in indhold[i].split(',')]
            if str(indholdList[0]) == ('"R"'):
                Bane, Test = baner(indholdList, path, mappe, fil_baner)
                BanerKlar.append(Test)
                continue
            else:
                Statuskode = SaetStatus(indholdList, Bane)
            
            if str(indholdList[0]) == (Bane):
                Deltager['Bane'] = indholdList[0]
                Deltager['Status'] = indholdList[1]
                Deltager['Statuskode'] = Statuskode
                Deltager['Placering'] = ""
                if efternavn_forst == 1:
                    Deltager['Navn'] = vendom(indholdList)
                else:
                    Deltager['Navn'] = indholdList[3]
                Deltager['Klub'] = indholdList[4]
                Deltager['Emit'] = indholdList[5]
                Deltager['Point'] = ""
                if len(indholdList) > 8:
                    Straktider = (indholdList[6:len(indholdList) - 2])
                    Minutter = str(datetime.timedelta(seconds=(Straktider[-3])))
                    Deltager['Tid'] = Minutter
                    Deltager['TidSek'] = Straktider[-3]
                    Strak = {}
                    Tid = 0
                    x = 1
                    for y in range (len(Straktider)):            
                        if y % 2 == 0:
                            ''' finder kontrol nummeret '''
                            Control = str('Post' + str(x) + ' - ' + str(Straktider[y]))
                            x = x + 1
                        else:
                            ''' finder tiden til kontrollen (sekunder) '''
                            Tid = Straktider[y]
                            Strak[Control] = Tid
                    Deltager['StrakTider'] = Strak
                else:
                    Deltager['Tid'] = 0
                    Deltager['StrakTider'] = 0
                
                ''' Skriver deltager til et dictionarie som til slut skrives til json fil '''
                DeltagerKlar.append(Deltager)
            Deltager = dict()
        #BanerKlar.append(Test)
        ''' Sorterer deltagerne efter bane og tid '''
        DeltagerKlar = sorted(DeltagerKlar, key = lambda i: (i['Bane'], i['Statuskode'], i['Tid']))
        #print (Deltagerklar)
        #DeltagerKlar = sorted(DeltagerKlar, key = lambda i: (i['Status']), reverse=True)

        with open(path + mappe + '\\' + fil_baner, 'w', encoding='utf8') as PostBaner:
            PostBaner.write(json.dumps(BanerKlar))

        with open(path + mappe + '\\' + fil_bearbejdet, 'w', encoding='utf8') as DeltagerSkriv:
            DeltagerJson = json.dumps(DeltagerKlar, ensure_ascii=False)
            DeltagerSkriv.write(DeltagerJson)

    done = "Gennemført beregn1"
    return done