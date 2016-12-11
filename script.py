#!/usr/bin/python
import os, sys, time
from subprocess import call
import piwigo
 
time.sleep(20)
shot_in_sec = [0, 30]
lt = time.localtime()
path = '/run/'
mysite = piwigo.Piwigo('http://piwigo.lkcm.eu')
user = 'ljozsa'
passwd = ''
mysite.pwg.session.login(username=user, password=passwd)
cam_name = 'hangar2'    

def get_cat_id(name,cat_id=None):
    for cat in mysite.pwg.categories.getList(cat_id=cat_id)['categories']:
        if cat['name'] == name:
            return cat['id']

root_id = get_cat_id(cam_name)
if not root_id:
    root_id = mysite.pwg.categories.add(name=cam_name)['id']

album_names = [cat['name'] for cat in \
 mysite.pwg.categories.getList(cat_id=root_id)['categories']]

while(True):
    lt = time.localtime()
    if lt.tm_sec in shot_in_sec:
        if lt.tm_min == 0 and lt.tm_sec == 0:
            album_names = [cat['name'] for cat in \
                mysite.pwg.categories.getList(cat_id=root_id)['categories']]
            if time.strftime("%Y-%m-%d-%H:00", lt) not in album_names:
                res = mysite.pwg.categories.add(\
                 name=time.strftime("%Y-%m-%d-%H:00", lt),parent=root_id)['id']
        # if ran for the first time
        if time.strftime("%Y-%m-%d-%H:00", lt) not in album_names: 
            res = mysite.pwg.categories.add(\
                 name=time.strftime("%Y-%m-%d-%H:00", lt),parent=root_id)['id']
        else:
            res = get_cat_id(time.strftime("%Y-%m-%d-%H:00", lt),root_id)

        call(["/usr/bin/raspistill", "-w", "720", "-h", "540",
            "-o", path + "pic.jpg"])
        mysite.pwg.images.addSimple(category=res, name=\
            time.strftime("%Y-%m-%d-%H:%M:%S", lt),
            image=path + "pic.jpg")

    time.sleep(1)
