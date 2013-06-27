#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.4"
__author__ = "Pavel Yegorov"

import suds
from base64 import b64encode

API_URL = "http://www.zapret-info.gov.ru/services/OperatorRequest/?wsdl"

class ZapretInfo:
    def getLastDumpDate(self):
        client = suds.client.Client(API_URL)
        result=client.service.getLastDumpDate()
        return result

    def sendRequest(self,requestFile,signatureFile):
        file = open(requestFile, "rb")
        data = file.read()
        file.close()
        xml = b64encode(data)

        file = open(signatureFile, "rb")
        data = file.readlines()
        file.close()

        if '-----' in data[0]:
            sert = ''.join(data[1:-1])
        else:
            sert = ''.join(data)
	sert = b64encode(sert)
			
        client = suds.client.Client(API_URL)
        result=client.service.sendRequest(xml,sert)

        return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)

    def getResult(self,code):
        client = suds.client.Client(API_URL)
        result=client.service.getResult(code)

        return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)
