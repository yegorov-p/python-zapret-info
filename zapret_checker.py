#!/usr/bin/env python
# -*- coding: utf-8 -*-
# yegorov.p@gmail.com

from xml.etree.ElementTree import ElementTree
from datetime import datetime
from zapretinfo import ZapretInfo
import time
import zipfile
from base64 import b64decode
import argparse
import os.path
import logging
import hashlib

parser = argparse.ArgumentParser(add_help=True, description='Downloads list of restricted websites')
parser.add_argument("-r", "--request", action="store", required=True, type=str,
                    help="full path to request.xml file")
parser.add_argument("-s", "--signature", action="store", required=True, type=str,
                    help="full path to digital signature file (in PKCS#7 format)")
parser.add_argument("-l", "--log", action="store", required=False, type=str,
                    default='rkn_dump.log',
                    help="log filename")

args = parser.parse_args()

XML_FILE_NAME = args.request
P7S_FILE_NAME = args.signature
LOG_FILE_NAME = args.log

logging.basicConfig(filename=LOG_FILE_NAME, filemode='a',
                    format=u'%(asctime)s  %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Starting script.')
logger.info('Check if dump.xml already exists.')
if os.path.exists('dump.xml'):
    logger.info('dump.xml already exists.')
    data = ElementTree().parse("dump.xml")

    dt = datetime.strptime(data.attrib['updateTime'][:19], '%Y-%m-%dT%H:%M:%S')
    updateTime = int(time.mktime(dt.timetuple()))
    logger.info('Got updateTime: %s.', updateTime)

    dt = datetime.strptime(data.attrib['updateTimeUrgently'][:19], '%Y-%m-%dT%H:%M:%S')
    updateTimeUrgently = int(time.mktime(dt.timetuple()))
    logger.info('Got updateTimeUrgently: %s.', updateTimeUrgently)

    fromFile = max(updateTime, updateTimeUrgently)
    logger.info('Got latest update time: %s.', fromFile)
else:
    logger.info('dump.xml does not exist')
    fromFile = 0

session = ZapretInfo()

logger.info('Check if dump.xml has updates since last sync.')
last_dump = session.getLastDumpDateEx()
logger.info('Current versions: webservice: %s, dump: %s, doc: %s',
            last_dump.webServiceVersion,
            last_dump.dumpFormatVersion,
            last_dump.docVersion)
if max(last_dump.lastDumpDate, last_dump.lastDumpDateUrgently) / 1000 <> fromFile:
    logger.info('New dump is available.')
    logger.info('Sending request.')
    request = session.sendRequest(XML_FILE_NAME, P7S_FILE_NAME, '2.1')
    logger.info('Checking request status.')
    if request['result']:
        code = request['code']
        logger.info('Got code %s', code)
        time.sleep(60)
        logger.info('Waiting for a minute.')
        while 1:
            logger.info('Trying to get result...')
            request = session.getResult(code)
            if request['result']:
                logger.info('Got a dump ver. %s for the %s (INN %s)',
                            request['dumpFormatVersion'],
                            request['operatorName'].decode('utf-8'),
                            request['inn'])
                with open('result.zip', "wb") as f:
                    f.write(b64decode(request['registerZipArchive']))
                logger.info('Downloaded dump %d bytes, MD5 hashsum: %s',
                            os.path.getsize('result.zip'),
                            hashlib.md5(open('result.zip', 'rb').read()).hexdigest())
                try:
                    logger.info('Unpacking.')
                    zip_file = zipfile.ZipFile('result.zip', 'r')
                    zip_file.extract('dump.xml', '')
                    zip_file.extractall('./dumps/%s' % datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
                    zip_file.close()
                except zipfile.BadZipfile:
                    logger.error('Wrong file format.')
                break

            else:
                if request['resultCode'] == 0:
                    logger.info('Not ready yet. Waiting for a minute.')
                    time.sleep(60)
                else:
                    logger.error('Got an error, code %d: %s',
                                 request['resultCode'],
                                 request['resultComment'].decode('utf-8'))
                    break
    else:
        logger.error(request['resultComment'].decode('utf-8'))
else:
    logger.info('No updates.')
logger.info('Script stopped.')
