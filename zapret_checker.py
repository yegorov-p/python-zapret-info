#!/usr/bin/env python
# -*- coding: utf-8 -*-
# yegorov-p.ru
from xml.etree.ElementTree import ElementTree
from datetime import datetime,timedelta
from zapretinfo import ZapretInfo
import time
import zipfile
from base64 import b64decode



XML_FILE_NAME = "req.xml"
P7S_FILE_NAME = "req.xml.p7s"

#Если файлик ранее выгружался, то пробуем получить из него данные
try:
    ts=ElementTree().parse("dump.xml").attrib['updateTime']
    dt = datetime.strptime(ts[:19],'%Y-%m-%dT%H:%M:%S')
    fromFile=int(time.mktime(dt.timetuple()))
except:
    fromFile=0

opener=ZapretInfo()

#Проверяем, изменился ли файлик
if opener.getLastDumpDate()/1000<>fromFile:
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

                zip_file = zipfile.ZipFile('result.zip', 'r')
                zip_file.extract('dump.xml', '')
                zip_file.close()
                break
            else:
                #Архив не получен, проверяем причину.
                if request['resultComment']=='запрос обрабатывается':
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
