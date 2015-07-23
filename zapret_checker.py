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

parser = argparse.ArgumentParser(
    add_help=True, description='Downloads list of restricted websites')
parser.add_argument("-r", "--request", action="store", required=False, type=str,
                    help="full path to request.xml file")
parser.add_argument(
    "-s",
    "--signature",
    action="store",
    required=False,
    type=str,
    help="full path to digital signature file (in PKCS#7 format)")

parser.add_argument("-l", "--log", action="store", required=False, type=str,
                    default='rkn_dump.log',
                    help="log filename")

parser.add_argument("-t", "--time", action="store_true", required=False,
                    default=False,
                    help="show last dump date")

parser.add_argument("-d", "--dir", action="store", required=False, type=str,
                    default='./dumps',
                    help="path to dumps directory")

parser.add_argument("-n", "--no_archives", action="store_true", required=False,
                    default=False,
                    help="do not save archives")

args = parser.parse_args()

XML_FILE_NAME = args.request
P7S_FILE_NAME = args.signature
LOG_FILE_NAME = args.log


def main():
    session = ZapretInfo()

    if args.time:
        last_dump = session.getLastDumpDateEx()
        last_dump_date = max(last_dump.lastDumpDate, last_dump.lastDumpDateUrgently) / 1000
        print last_dump_date
    else:
        logging.basicConfig(filename=LOG_FILE_NAME, filemode='a',
                            format=u'%(asctime)s  %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info('Starting script.')

        if not XML_FILE_NAME:
            logging.error('No XML file.')
            print 'No XML file.'
            return

        if not P7S_FILE_NAME:
            logging.error('No signature file.')
            print 'No signature file.'
            return

        try:
            os.mkdir(args.dir)
        except OSError:
            pass

        logger.info('Check if dump.xml already exists.')
        if os.path.exists('dump.xml'):
            logger.info('dump.xml already exists.')
            data = ElementTree().parse("dump.xml")

            dt = datetime.strptime(data.attrib['updateTime'][:19], '%Y-%m-%dT%H:%M:%S')
            updateTime = int(time.mktime(dt.timetuple()))
            logger.info('Got updateTime: %s.', updateTime)

            dt = datetime.strptime(
                data.attrib['updateTimeUrgently'][:19], '%Y-%m-%dT%H:%M:%S')
            updateTimeUrgently = int(time.mktime(dt.timetuple()))
            logger.info('Got updateTimeUrgently: %s.', updateTimeUrgently)

            fromFile = max(updateTime, updateTimeUrgently)
            logger.info('Got latest update time: %s.', fromFile)
        else:
            logger.info('dump.xml does not exist')
            fromFile = 0

        logger.info('Check if dump.xml has updates since last sync.')
        last_dump = session.getLastDumpDateEx()
        logger.info('Current versions: webservice: %s, dump: %s, doc: %s',
                    last_dump.webServiceVersion,
                    last_dump.dumpFormatVersion,
                    last_dump.docVersion)
        if max(last_dump.lastDumpDate, last_dump.lastDumpDateUrgently) / \
                1000 != fromFile:
            logger.info('New dump is available.')
            logger.info('Sending request.')
            request = session.sendRequest(XML_FILE_NAME, P7S_FILE_NAME, '2.2')
            logger.info('Checking request status.')
            if request['result']:
                code = request['code']
                logger.info('Got code %s', code)
                time.sleep(60)
                logger.info('Waiting for a minute.')
                while True:
                    logger.info('Trying to get result...')
                    request = session.getResult(code)
                    if request['result']:
                        logger.info('Got a dump ver. %s for the %s (INN %s)',
                                    request['dumpFormatVersion'],
                                    request['operatorName'].decode('utf-8'),
                                    request['inn'])
                        with open('result.zip', "wb") as f:
                            f.write(b64decode(request['registerZipArchive']))
                        logger.info(
                            'Downloaded dump %d bytes, MD5 hashsum: %s',
                            os.path.getsize('result.zip'),
                            hashlib.md5(
                                open(
                                    'result.zip',
                                    'rb').read()).hexdigest())
                        try:
                            logger.info('Unpacking.')
                            zip_file = zipfile.ZipFile('result.zip', 'r')
                            zip_file.extract('dump.xml', '')
                            if not args.no_archives:
                                zip_file.extractall(
                                    '%s/%s' %
                                    (args.dir, datetime.now().strftime("%Y-%m-%dT%H-%M-%S")))
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

if __name__ == '__main__':
    main()
