#!/usr/bin/python
import os, sys, time
from subprocess import call
 
shot_in_sec = [0, 30]
lt = time.localtime()
path = sys.argv[1] 
full_path = path + '/' + time.strftime("%Y-%m-%d-%H:00", lt)
if not os.path.exists(full_path):
    os.makedirs(full_path)
     
while(True):
    lt = time.localtime()
    if lt.tm_sec in shot_in_sec:
        if lt.tm_min == 0 and lt.tm_sec == 0:
            full_path = path + '/' + time.strftime("%Y-%m-%d-%H:%M", lt) 
            if not os.path.exists(full_path):
                os.makedirs(full_path)
        precise_time = time.strftime("%Y-%m-%d-%H:%M:%S", lt)
        call(["/usr/bin/raspistill", "-w", "720", "-h", "540", 
"-o", full_path + "/" + precise_time + ".jpg"])
        spl = path.split('/')
        if spl[-1] == '':
            spl.pop()
            append_blank = True
        else:
            append_blank = False
        last = spl.pop()
        spl.extend(('_sfpg_data', 'thumb', last, 
time.strftime("%Y-%m-%d-%H:00", lt)))

        if append_blank == True:
            spl.append('')

        if not os.path.exists("/".join(spl)):
            os.makedirs("/".join(spl))

        call(["/usr/local/bin/epeg", "-w", "160", "-h", "120", "-q", "75",
full_path + '/' + precise_time + ".jpg", "/tmp/temp.jpg"])
        call(["/usr/bin/convert", "/tmp/temp.jpg", "-pointsize", "9", "-fill",
"white", "-annotate", "+10+20", precise_time, "/".join(spl) + "/" +
precise_time + ".jpg" ])
        base_path = path
        base_path = path.rstrip('/').split('/')
        base_path.pop()
        call(["/usr/bin/chown", "-R", "apache.apache", "/".join(base_path)])

        time.sleep(1)

