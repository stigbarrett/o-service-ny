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
import os
from math import radians, cos, sin, asin, sqrt


plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

def distance_from(loc1,loc2): 
    dist=hs.haversine(loc1,loc2,unit='m')
    return round(dist,2)

def find_postpassage():
    pass

def change(s, a, b):
    s[b], s[a] = s[a], s[b]

#def beregn_gpx(gemt_gpx_fil, post_data, gemt_resultat_fil, gemt_spor_fil, bane_gpx, navn_gpx):
#(gpx, post_data, bane_gpx, navn_gpx)
def beregn_gpx(gpx, post_data, bane_gpx, navn_gpx):
    
    #with open(gemt_gpx_fil, 'r') as gpx_file:
    #    gpx = gpxpy.parse(gpx_file)

    poster_loc = []
    
    #with open(gemt_poster_fil, 'r', encoding='utf-8') as poster:
    #    json_file = json.load(poster)
        
    for row in post_data:
        poster = {}
        poster['Post'] = row['Post']
        poster['Postnr'] = row['Postnr']
        poster['coor'] = row['coor']
        poster_loc.append(poster)

    for i, enhed in enumerate(poster_loc):
        if i == 0:
            start_post = enhed['coor']
            enhed['afstand_fra'] = 0
            enhed['samlet_afstand'] = 0
            samlet_afstand = 0
        else:
            naste_post = enhed['coor']
            afstand = distance_from(start_post, naste_post)
            samlet_afstand = samlet_afstand + afstand
            enhed['afstand_fra'] = afstand
            enhed['samlet_afstand'] = samlet_afstand
            start_post = enhed['coor']

    route_info = []
    route = []
    for track in gpx.tracks:
        for segment in track.segments:
            for s, point in enumerate(segment.points):
                    temp = {}
                    d = datetime.fromisoformat(str(point.time))
                    timeconv = d.strftime('%H:%M:%S')
                    temp['nr'] = s
                    temp['latitude'] = point.latitude
                    temp['longitude'] = point.longitude
                    temp['time'] = point.time
                    temp['tid'] = timeconv
                    temp['coor'] = [point.latitude, point.longitude]
                    if s != 0:
                        afstand_coor = [point.latitude, point.longitude]
                        afstand = distance_from(afstand_coor,gl_afstand_coor)
                        temp_afstand = temp_afstand + afstand
                        temp['afstand'] = afstand
                        temp['samlet_afstand'] = temp_afstand
                        gl_afstand_coor = [point.latitude, point.longitude]
                    else:
                        temp_afstand = 0
                        temp['afstand'] = 0
                        temp['samlet_afstand'] = 0
                        gl_afstand_coor = [point.latitude, point.longitude]
                    route.append({
                        'latitude': point.latitude,
                        'longitude': point.longitude,
                        'time': timeconv,
                        'coor': [point.latitude, point.longitude]
                    })
                    route_info.append(temp)

    #route_df = pd.DataFrame(route_info)
    #route_df.to_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\minvalues_Bane4_hele.csv', index=False)

    correct_inputs = poster_loc
    user_inputs = route_info
    reduced_user_inputs = user_inputs
    validated_inputs = []
    postpaseret = []

    def indenfor(lon1, lat1, lon2, lat2):
        #def haversine():
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r
    
    def paa_vej(center_point, test_point):
        #center_point = [{'lat': -7.7940023, 'lng': 110.3656535}]
        #test_point = [{'lat': -7.79457, 'lng': 110.36563}]

        lat1 = center_point[0]['lat']
        lon1 = center_point[0]['lng']
        lat2 = test_point[0]['lat']
        lon2 = test_point[0]['lng']

        #radius = 1.00 # in kilometer
        #radius = 0.060

        a = indenfor(lon1, lat1, lon2, lat2)

        #print('Distance (km) : ', a)
        #if a <= radius:
        #    b = True
        #    print('Inside the area')
        #else:
        #    b = False
        #    print('Outside the area')
        
        return a

    #def find_result(correct, reduced_user_inputs, correct_naste, var_i):
    def find_result(correct, reduced_user_inputs, var_i):
        if 'spor_slice' in locals():
            pass
        else:
            spor_slice = []
        
        gl_afstand = 3000
        #if correct['Post'] == 'F1':
        #    max_afstand = (correct_naste['samlet_afstand'])
        #else:
        #    max_afstand = ((correct_naste['samlet_afstand'])/100)*80
        #if correct_naste['Post'] != 'F1':
        #    max_afstand = ((correct_naste['samlet_afstand'])/100)*80
        #elif correct['Post'] == 'F1':
        #    max_afstand = (correct_naste['samlet_afstand'])
        #else:
        #    max_afstand = 0
        gl_afstand = 60
        negativ_afstand = 0
        bevagelse = 0
        #gpx_nummer = reduced_user_inputs['nr']
        post_point_dict = {}
        gpx_point_dict = {}
        gpx_point_list = []
        post_point_list = []
        x = 1
        for idx, user_input in enumerate(reduced_user_inputs):
            #center_point = [{'lat': -7.7940023, 'lng': 110.3656535}]
            #test_point = [{'lat': -7.79457, 'lng': 110.36563}]
            post_point_dict['lat'] = correct['coor'][0]
            post_point_dict['lng'] = correct['coor'][1]
            post_point_list.append(post_point_dict)
            gpx_point_dict['lat'] = user_input['latitude']
            gpx_point_dict['lng'] = user_input['longitude']
            gpx_point_list.append(gpx_point_dict)
            er_det = paa_vej(post_point_list, gpx_point_list)
            #radius = 0.060
            radius = 0.6
            if idx == 0:
                temp_var = user_input['nr']
               
            if er_det <= radius:
                #print('ok' + str(idx))
                
                if x > 1:
                    if user_input['nr'] > temp_var + 100:
                        break
                user_input['afstand_post'] = er_det * 1000
                spor_slice.append(user_input)
                temp_var = user_input['nr']
                user_input['temp_nr'] = idx
                temp_var = user_input['nr']
                if x == 26:
                    pass
                x = x + 1
        
        if len(spor_slice) == 0:
            print(spor_slice)
        for val in spor_slice:
            
            if val['afstand_post']:
                pass
            else:
                print(val['afstand_post'])
        
        mindste_afstand = min(spor_slice, key=lambda x:x['afstand_post'])
        max_idx = mindste_afstand['temp_nr']
        
        reduced_user_inputs=reduced_user_inputs[max_idx+1:]
        return {'result': correct, 'reduced_user_inputs': reduced_user_inputs, 'afstand': gl_afstand, 'validated': mindste_afstand}

    for i, correct in enumerate(correct_inputs):
        temp1 = {}
        #print(len(reduced_user_inputs))
        #stop_var = len(correct_inputs)
        #if i + 1 < stop_var:
        #    correct_naste = correct_inputs[i + 1]
        #else:
        #    correct_naste = correct_inputs[i]
        #result = find_result(correct, reduced_user_inputs, correct_naste, i)
        result = find_result(correct, reduced_user_inputs, i)
        #print(len(reduced_user_inputs))
        reduced_user_inputs = result['reduced_user_inputs']
        #print(result['result']['Post'])
        #antal_point2 = len(reduced_user_inputs)
        postpaseret.append(result['validated'])
        #gl_afstand = result['gl_afstand']
        if result['validated'] != 'ej':
            validated_inputs.append(result['result'])
            temp1 = result['validated']
            temp1['afstand'] = result['afstand']
            #postpaseret.append(temp1)

    def lobet_distance(postnr, gl_postnr):
        yx = 0
        for i, hvert in enumerate(route_info):
            
            if hvert['nr'] >= gl_postnr and hvert['nr'] <= postnr:
                if yx == 0:
                    temp_afstand = 0
                    hvert_gammel = hvert['coor']
                    afstand = 0
                    yx = yx + 1
                else:
                    temp_afstand = distance_from(hvert['coor'], hvert_gammel)
                    hvert_gammel = hvert['coor']
                    afstand = afstand + temp_afstand
                    yx = yx + 1
        return afstand

    afstand = []
    afstandAlle = []
    afstandAlle.append(navn_gpx)
    afstandAlle.append(bane_gpx)
    y = 1
    StatusData = 0
    for a, post in enumerate(postpaseret):
        temtp1 = {}
        minAfstandItem={}
        postnr = "Post" + str(a)
        #minAfstandItem = min(route_info, key=lambda x:x[postnr])
        tid10 = post['time']
        tid = tid10.timestamp()
        afstand_til = post['afstand_post']
        minAfstandItem['Post'] = postnr
        if afstand_til > 30:
            minAfstandItem['Status'] = 'ejOK'
            StatusData = 1
            #afstandAlle.append('Disk')
        else:
            minAfstandItem['Status'] = 'OK'
            #afstandAlle.append('OK')
        minAfstandItem['Afstand_fra'] = afstand_til
        minAfstandItem['latitude'] = post['latitude']
        minAfstandItem['longitude'] = post['longitude']
        if y == 1:
            minAfstandItem['tidsek'] = 0
            minAfstandItem['tid'] = "00:00"
            minAfstandItem['afstandTil'] = 0
            minAfstandItem['samletAfstandTil'] = 0
            afstandtilMeter = 0
            samletAfstandMeter = 0
            post_nr_gammel = 0
            samletT = 0
            samletTid = 0
            tid_gammel = tid
        else:
            sekunder = (tid - tid_gammel)
            #a = datetime.timedelta(seconds=sekunder)
            a = time.strftime('%H:%M:%S', time.gmtime(sekunder))
            afstandtilMeter = lobet_distance(post['nr'], post_nr_gammel)
            minAfstandItem['afstandTil'] = afstandtilMeter
            samletAfstandMeter = samletAfstandMeter + afstandtilMeter
            minAfstandItem['samletAfstandTil'] = samletAfstandMeter
            minAfstandItem['tidsek'] = sekunder
            minAfstandItem['tid'] = a
            samletT = samletT + sekunder
            samletT2 = time.strftime('%H:%M:%S', time.gmtime(samletT))
            minAfstandItem['tidSamletSek'] = samletT
            minAfstandItem['tidSamlet'] = samletT2
            samletTid = samletTid + sekunder
            tid_gammel = tid
            post_nr_gammel = post['nr']
        y=y+1
        temtp1["post"] = minAfstandItem
        afstand.append(minAfstandItem)
    if StatusData == 0:
        afstandAlle.append('OK')
    else:
        afstandAlle.append['ejOK']
    afstandAlle.append(afstand)
    kontrolJson = json.dumps(afstandAlle)
    spor = json.dumps(route)
    #with open(gemt_resultat_fil, 'w', encoding='utf8') as kontrolSkriv:
    #    
    #    kontrolSkriv.write(kontrolJson)

    #with open(gemt_spor_fil, 'w', encoding='utf8') as gemt_spor:
    #    
    #    gemt_spor.write(spor)
    
    return kontrolJson, spor, StatusData
    
#def start_gpx(gemt_gpx_fil, post_data, gemt_resultat_fil, gemt_spor_fil, bane_gpx, navn_gpx):
#def start_gpx(gpx, post_data, gemt_resultat_fil, gemt_spor_fil, bane_gpx, navn_gpx):
def start_gpx(gpx, post_data, bane_gpx, navn_gpx):
    #beregnet = beregn_gpx(gemt_gpx_fil, gemt_poster_fil, gemt_resultat_fil, gemt_spor_fil, bane_gpx, navn_gpx)
    #beregnet = beregn_gpx(gemt_gpx_fil, post_data, gemt_resultat_fil, gemt_spor_fil, bane_gpx, navn_gpx)
    beregnet = beregn_gpx(gpx, post_data, bane_gpx, navn_gpx)
    return beregnet

#def create_map(spor_fil, post_data, gemt_resultat_fil, kort_data, bane, path):
def create_map(gpx_spor, post_data, resultat_data, kort_data, bane, path):
    
    #with open(kort_fil, 'r', encoding='utf8') as kort_file:
    kortoplysning = kort_data
    resultat_data = list(resultat_data)
    
    #for kort in kortoplysning['kort']:
    if bane in kortoplysning[0]['baneliste']:
        min_lon = float(kortoplysning[0]['min_lon'])
        max_lon = float(kortoplysning[0]['max_lon'])
        min_lat = float(kortoplysning[0]['min_lat'])
        max_lat = float(kortoplysning[0]['max_lat'])
        kortfilen = kortoplysning[0]['kortfil']
    
    if type(gpx_spor) == list:
        spor = gpx_spor
    elif type(gpx_spor) == str:
        spor = gpx_spor
    else:
        with open(gpx_spor, 'r', encoding='utf8') as spor_file:
            spor = json.load(spor_file)
    
    #with open(poster_fil, 'r', encoding='utf8') as poster_file:
    poster = post_data
    
    if type(resultat_data) == list:
        resultatet = resultat_data
    elif type(resultat_data) == str:
        resultatet = resultat_data
    else:
        with open(resultat_data, encoding='utf8') as resultat:
            resultatet = json.load(resultat)[2]
    
    sted = {}
    #for a, post in enumerate(poster['Bane 2']):
    #for a, post in enumerate(poster[bane]):
    for a, post in enumerate(poster):
        sted[a] = a
        sted['latitude'] = post['coor'][0]
        sted['longtitude'] = post['coor'][1]
        latitude = post['coor'][0]
        longitude = post['coor'][1]

    #m = folium.Map(location=[int(sted['latitude']).mean(), int(sted['longitude']).mean()], zoom_start=16, tiles='OpenStreetMap', width=1200, height=800)
    m = folium.Map(location=[latitude, longitude], zoom_start=14, tiles='OpenStreetMap', width='100%', height=800)
    kortfilen = kortfilen.replace('/', '\\')
    kort_billede = os.path.join(path, kortfilen)
    img_overlay = folium.raster_layers.ImageOverlay(image=kort_billede, bounds=[[min_lat, min_lon], [max_lat, max_lon]])
    img_overlay.add_to(m)
    
    '''! postcirklerne i forhold til sporet '''
    
    for _, row in enumerate(resultatet):
        if str(row['Status']) == 'OK':
            statuscolor='green',
        else:
            statuscolor='red',

        folium.CircleMarker(
            location= [row['latitude'],row['longitude']],
            radius=15,
            #popup= row[['Condition','Location']],
                color=statuscolor,
                fill=True,
                fill_color=statuscolor
            ).add_to(m)

    '''# Posternes faktiske placering'''
    #for _, row in enumerate(poster[bane]):
    for _, row in enumerate(poster):
        statuscolor='red',
        folium.Marker(
            location = [row['coor'][0], row['coor'][1]],
            popup = 'post ' + str(row['Postnr']),
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)

    '''# selve sporets visning'''
    coordinates = []
    for punkt in spor:
        coordinates.append(punkt['coor'])
    #coordinates = [tuple(x) for x in route_df[['latitude', 'longitude']].to_numpy()]
    folium.PolyLine(coordinates, weight=5).add_to(m)
    #m.add_children(plugins.ImageOverlay(kort, opacity=0.8, bounds =[[min_lat, min_lon], [max_lat, max_lon]]))
    return m

def omdan_spor(spor_fil):
    #with open('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\Bane_2_Undallslund_uge_25.gpx', 'r') as gpx_file:
    with open(spor_fil, 'r') as gpx_file:
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

    route_df.to_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\MapRun_Bane_2_Undallslund_uge_25_i_2022_PXAC.csv', index=False)

    #cust_loc=pd.read_excel('customer_location.xlsx')
    #hotel_loc=pd.read_excel("Hotel_location.xlsx")

    spor_loc=pd.read_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\MapRun_Bane_2_Undallslund_uge_25_i_2022_PXAC.csv')
    #poster_loc=pd.read_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\Bane2.csv')

    spor_loc['coor'] = list(zip(spor_loc.latitude, spor_loc.longitude))
    #poster_loc['coor'] = list(zip(poster_loc.latitude, poster_loc.longitude))

    return route_info

def omdan_poster():
    poster_loc=pd.read_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\Bane2.csv')
    poster_loc['coor'] = list(zip(poster_loc.latitude, poster_loc.longitude))