#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.7"
__author__ = "Pavel Yegorov"

import suds
from base64 import b64encode

API_URL = "http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl"
# API_URL = "http://vigruzki.rkn.gov.ru/services/OperatorRequestTest/?wsdl"

class ZapretInfo(object):
    def getLastDumpDateEx(self):
        '''
        Оставлен для совместимости. Аналогичен getLastDumpDateEx, но возвращает только один
        параметр lastDumpDate.
        '''
        client = suds.client.Client(API_URL)
        result = client.service.getLastDumpDateEx()
        return result

    def getLastDumpDate(self):
        '''
        Метод предназначен для получения временной метки последнего обновления выгрузки из реестра,
        а также для получения информации о версиях веб-сервиса, памятки и текущего формата выгрузки.
        '''
        client = suds.client.Client(API_URL)
        result = client.service.getLastDumpDate()
        return result

    def sendRequest(self, requestFile, signatureFile, versionNum=2.0):
        '''
        Метод предназначен для направления запроса на получение выгрузки из реестра.
        '''
        with open(requestFile, "rb") as f:
            data = f.read()

        xml = b64encode(data)

        with open(signatureFile, "rb") as f:
            data = f.readlines()

        if '-----' in data[0]:
            sert = ''.join(data[1:-1])
        else:
            sert = ''.join(data)

        sert = b64encode(sert)
        client = suds.client.Client(API_URL)
        result = client.service.sendRequest(xml, sert, versionNum)

        return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)

    def getResult(self, code):
        '''
        Метод предназначен для получения результата обработки запроса - выгрузки из реестра
        '''
        client = suds.client.Client(API_URL)
        result = client.service.getResult(code)

        return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)
