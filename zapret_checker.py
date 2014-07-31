#!/usr/bin/env python
# -*- coding: utf-8 -*-
# yegorov-p.ru

from xml.etree.ElementTree import ElementTree
from datetime import datetime,timedelta
from zapretinfo import ZapretInfo
import time
import zipfile
from base64 import b64decode
import json
import xml.etree.ElementTree as etree
import ipcalc

XML_FILE_NAME = "req_new.xml"
P7S_FILE_NAME = "request.xml.sign"

#Если файлик ранее выгружался, то пробуем получить из него данные
dt = datetime.strptime(ElementTree().parse("dump.xml").attrib['updateTime'][:19],'%Y-%m-%dT%H:%M:%S')
updateTime=int(time.mktime(dt.timetuple()))
try:
    dt = datetime.strptime(ElementTree().parse("dump.xml").attrib['updateTimeUrgently'][:19],'%Y-%m-%dT%H:%M:%S')
    updateTimeUrgently=int(time.mktime(dt.timetuple()))
except:
    updateTimeUrgently=0
fromFile = max(updateTime,updateTimeUrgently)

opener=ZapretInfo()

#Проверяем, изменился ли файлик
if max(opener.getLastDumpDateEx().lastDumpDate, opener.getLastDumpDateEx().lastDumpDateUrgently)/1000<>fromFile:
    #Файлик изменился. Отправляем запрос на выгрузку
    request=opener.sendRequest(XML_FILE_NAME,P7S_FILE_NAME)
    #Проверяем, принят ли запрос к обработке
    if request['result']:
        #Запрос не принят, получен код
        code=request['code']
        print 'Got code %s' % (code)
        print 'Trying to get result...'
        while 1:
            #Пытаемся получить архив по коду
            request=opener.getResult(code)
            if request['result']:
                #Архив получен, скачиваем его и распаковываем
                print 'Got it!'
                file = open('result.zip', "wb")
                file.write(b64decode(request['registerZipArchive']))
                file.close()

                try:
                    zip_file = zipfile.ZipFile('result.zip', 'r')
                    zip_file.extract('dump.xml', '')
                    zip_file.extractall('./dumps/%s'%datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    zip_file.close()
                    break
                    
                except :
                    print 'Wrong file format'
                break
            else:
                #Архив не получен, проверяем причину.
                if request['resultCode']==0:
                    #Если это сообщение об обработке запроса, то просто ждем минутку.
                    print 'Not ready yet.'
                    time.sleep(60)
                else:
                    #Если это любая другая ошибка, выводим ее и прекращаем работу
                    print 'Error: %s' % request['resultComment']
                    break
    else:
        #Запрос не принят, возвращаем ошибку
        print 'Error: %s' % request['resultComment']
else:
    print 'No updates'
