#!/usr/bin/python
import os, sys, time, requests, pytz
from subprocess import call
from datetime import datetime
from glob import glob
from requests.exceptions import *
 
shot_in_sec = [0]
brn_lat = '49.2000'
brn_lon = '16.6167'
brn_tz = pytz.timezone('Europe/Prague')
utc_tz = pytz.timezone('UTC')

def get_sun(lat, lon):
    try:
        r = requests.get('http://api.sunrise-sunset.org/json?lat=' + lat + '&lng=' + lon + '=&formatted=0')
    except:
        r = None
    return r

def get_localized_time(time, tz): #time in format '%Y-%m-%dT%H:%M:%S+00:00'
    time_naive = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S+00:00')
    return tz.localize(time_naive)

def get_localized_time_now(tz):
    return tz.localize(datetime.now())


def get_cam_on_off(request):
    try:
        if r.json()['status'] == 'OK':
            civil_twilight_begin = r.json()['results']['civil_twilight_begin']
            civil_twilight_end = r.json()['results']['civil_twilight_end']
            cam_on = get_localized_time(civil_twilight_begin, utc_tz)
            cam_off = get_localized_time(civil_twilight_end, utc_tz)
        else:
            time_now = get_localized_time_now(utc_tz)
            cam_on = time_now.replace(hour=3, minute=0, second=0, microsecond=0)
            cam_off = time_now.replace(hour=20, minute=0, second=0, microsecond=0)
    except:
            time_now = get_localized_time_now(utc_tz)
            cam_on = time_now.replace(hour=3, minute=0, second=0, microsecond=0)
            cam_off = time_now.replace(hour=20, minute=0, second=0, microsecond=0)
    return cam_on, cam_off

time.sleep(20)  # allow chrony to sync
lt = get_localized_time_now(brn_tz)
path = sys.argv[1] 
full_path = path + '/' + datetime.strftime(lt, "%Y-%m-%d-%H:00")

try:
    r = get_sun(brn_lat, brn_lon)
except ConnectionError:
    time_now = get_localized_time_now(utc_tz)
    cam_on = time_now.replace(hour=3, minute=0, second=0, microsecond=0)
    cam_off = time_now.replace(hour=20, minute=0, second=0, microsecond=0)
else:
    cam_on, cam_off = get_cam_on_off(r)

sun_updated = False
     
while(True):
    lt = get_localized_time_now(brn_tz)
    if cam_on < lt and lt < cam_off:
        if lt.second in shot_in_sec:
            full_path = path + '/' + datetime.strftime(lt, "%Y-%m-%d-%H:00")
            if not os.path.exists(full_path):
                os.makedirs(full_path)
            precise_time = datetime.strftime(lt, "%Y-%m-%d-%H:%M:%S")
            call(["/usr/bin/raspistill", "-w", "720", "-h", "540", 
    "-o", full_path + "/" + precise_time + ".jpg"])
            call(["/usr/local/bin/epeg", "-w", "640", "-h", "480", "-q", "90",
    full_path + '/' + precise_time + ".jpg", "/tmp/hangar.jpg"])
            spl = path.split('/')
            if spl[-1] == '':
                spl.pop()
                append_blank = True
            else:
                append_blank = False
            last = spl.pop()
            spl.extend(('_sfpg_data', 'thumb', last,
    datetime.strftime(lt, "%Y-%m-%d-%H:00")))

            if append_blank == True:
                spl.append('')

            if not os.path.exists("/".join(spl)):
                os.makedirs("/".join(spl))

            call(["/usr/local/bin/epeg", "-w", "160", "-h", "120", "-q", "75",
    full_path + '/' + precise_time + ".jpg", "/run/temp.jpg"])

#            # create transparent canvas and add time there
#            call(["/usr/bin/convert", "-size", "160x120", "canvas:none",
#             "-undercolor", "black", "-pointsize", "9", "-fill", "white",
#             "-gravity", "NorthEast", "-annotate", "0", precise_time,
#             "/tmp/canvas.gif" ])
#
#            # join canvas and image thumbnail
#            call(["/usr/bin/composite", "/tmp/canvas.gif", "/run/temp.jpg",
#             "/".join(spl) + "/" + precise_time + ".jpg" ])
#            base_path = path
#            base_path = path.rstrip('/').split('/')
#            base_path.pop()
#            call(["/bin/chown", "-R", "www-data.www-data", "/".join(base_path)])
#
#            # create animated gif and place it to the galery root
#            jpeg_list = glob("/".join(spl) + "/*.jpg")
#            jpeg_list.append(full_path + "/_dir.gif")
#            jpeg_list.insert(0,"/usr/bin/convert")
#            call(jpeg_list)

    time.sleep(1)
    if lt.hour == 3 and lt.minute == 0 and sun_updated == False:
        r = get_sun(brn_lat, brn_lon)
        cam_on, cam_off = get_cam_on_off(r)
        sun_updated = True
    elif  lt.hour != 0:
        sun_updated = False


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
