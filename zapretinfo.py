#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.9"
__author__ = "yegorov.p@gmail.com"

import suds
from base64 import b64encode
import os

API_URL = "http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl"
# API_URL = "http://vigruzki.rkn.gov.ru/services/OperatorRequestTest/?wsdl"

class ZapretInfoException(RuntimeError):
    pass


class ZapretInfo(object):
    def __init__(self):
        self.cl = suds.client.Client(API_URL)

    def getLastDumpDateEx(self):
        '''
        Оставлен для совместимости. Аналогичен getLastDumpDateEx, но возвращает только один
        параметр lastDumpDate.
        '''
        result = self.cl.service.getLastDumpDateEx()
        return result

    def getLastDumpDate(self):
        '''
        Метод предназначен для получения временной метки последнего обновления выгрузки из реестра,
        а также для получения информации о версиях веб-сервиса, памятки и текущего формата выгрузки.
        '''
        result = self.cl.service.getLastDumpDate()
        return result

    def sendRequest(self, requestFile, signatureFile, versionNum='2.1'):
        '''
        Метод предназначен для направления запроса на получение выгрузки из реестра.
        '''
        if not os.path.exists(requestFile):
            raise ZapretInfoException('No request file')
        if not os.path.exists(signatureFile):
            raise ZapretInfoException('No signature file')

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
        result = self.cl.service.sendRequest(xml, sert, versionNum)

        return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)

    def getResult(self, code):
        '''
        Метод предназначен для получения результата обработки запроса - выгрузки из реестра
        '''
        result = self.cl.service.getResult(code)

        return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)
