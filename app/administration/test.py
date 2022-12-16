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

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

def distance_from(loc1,loc2): 
    dist=hs.haversine(loc1,loc2,unit='m')
    return round(dist,2)

def find_postpassage():
    pass

def change(s, a, b):
    s[b], s[a] = s[a], s[b]


with open('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\helle_morville.gpx', 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

poster_loc = []
with open('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\bane3.json', 'r') as poster:
    #reader = csv.reader(poster)
    #csv_file = csv.DictReader(poster)
    json_file = json.load(poster)
    
    for a, row in enumerate(json_file['Bane3']):
        #if a != 0:
        poster = {}
        poster['Post'] = row['Post']
        poster['Postnr'] = row['Postnr']
        #post['coor'] = [float(row['latitude']), float(row['longitude'])]
        poster['coor'] = row['coor']
        #change(poster['coor'], 0, 1)
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
for track in gpx.tracks:
    for segment in track.segments:
        for s, point in enumerate(segment.points):
                temp = {}
                #d = datetime.fromisoformat(point.time[:-1]).astimezone(timezone.utc)
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
                route_info.append(temp)

#route_df = pd.DataFrame(route_info)
#route_df.to_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\minvalues_Bane4_hele.csv', index=False)

#correct_inputs = post lokation
correct_inputs = poster_loc
#userinputs = spor = route_info
user_inputs = route_info
reduced_user_inputs = user_inputs
validated_inputs = []
postpaseret = []

def find_result(correct, reduced_user_inputs):
    spor_slice = []
    #spor_slice_ej = [] 
    gl_afstand = 3000
    bevagelse = 0
    for idx, user_input in enumerate(reduced_user_inputs):
        user_input['temp_nr'] = idx
        afstand = distance_from(correct['coor'], user_input['coor'])
        if afstand <= 30:
            bevagelse = bevagelse + user_input['afstand']
            user_input['afstand_post'] = afstand
            spor_slice.append(user_input)
            if bevagelse < 40:
                spor_slice.append(user_input)
                gl_afstand = afstand
            else:
                bevagelse = 0
                break
        
    #max_idx = max(item['temp_nr'] for item in spor_slice)
    mindste_afstand = min(spor_slice, key=lambda x:x['afstand_post'])
    max_idx = mindste_afstand['temp_nr']
    
    reduced_user_inputs=reduced_user_inputs[max_idx+1:]
    return {'result': correct, 'reduced_user_inputs': reduced_user_inputs, 'afstand': gl_afstand, 'validated': mindste_afstand}
    
antal_point = len(reduced_user_inputs)

for i, correct in enumerate(correct_inputs):
    temp1 = {}
    #print(len(reduced_user_inputs))
    result = find_result(correct, reduced_user_inputs)
    #print(len(reduced_user_inputs))
    reduced_user_inputs = result['reduced_user_inputs']
    #antal_point2 = len(reduced_user_inputs)
    postpaseret.append(result['validated'])
    #gl_afstand = result['gl_afstand']
    if result['validated'] != 'ej':
        validated_inputs.append(result['result'])
        temp1 = result['validated']
        temp1['afstand'] = result['afstand']
        #postpaseret.append(temp1)

afstand = []
afstandAlle = []
y = 1
for a, post in enumerate(postpaseret):
    temtp1 = {}
    minAfstandItem={}
    postnr = "Post" + str(a)
    #minAfstandItem = min(route_info, key=lambda x:x[postnr])
    tid10 = post['time']
    tid = tid10.timestamp()
    afstand_til = post['afstand_post']
    minAfstandItem['coor'] = post['coor']
    #tid = sum(int(x) * 60 ** i for i, x in enumerate(reversed((str(minAfstandItem.tid)).split(':'))))
    #tid = spor.time
    minAfstandItem['Post'] = postnr
    if afstand_til > 30:
        minAfstandItem['Status'] = 'ejOK'
    else:
        minAfstandItem['Status'] = 'OK'
    minAfstandItem['Afstand_fra'] = afstand_til
    if y == 1:
        minAfstandItem['tid'] = "00:00:00"
        samletT = 0
        samletTid = 0
        tid_gammel = tid
    else:
        sekunder = (tid - tid_gammel)
        #a = datetime.timedelta(seconds=sekunder)
        a = time.strftime('%H:%M:%S', time.gmtime(sekunder))
        minAfstandItem['tid'] = a
        samletT = samletT + sekunder
        samletT2 = time.strftime('%H:%M:%S', time.gmtime(samletT))
        minAfstandItem['tidSamlet'] = samletT2
        samletTid = samletTid + sekunder
        tid_gammel = tid
    y=y+1
    temtp1["post"] = minAfstandItem

    #temtp1[minAfstandItem]
    afstand.append(minAfstandItem)
afstandAlle.append(afstand)

with open('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\resultat_bane1.csv', 'w', newline='') as file:
    fieldnames = ['coor', 'Post', 'Status', 'Afstand_fra', 'tid', 'tidSamlet']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for line in afstand:
        writer.writerow(line)

print('s')
#route_df = pd.DataFrame(afstand)

#route_df.to_csv('C:\\Users\\sba\\OneDrive\\Dokumenter\\Python40\\Ny_Orientering\\app\\static\\minvalues_Bane4.csv', index=False)



