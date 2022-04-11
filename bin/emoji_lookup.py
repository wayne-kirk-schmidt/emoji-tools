#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exaplanation: emoji_lookup. Build the Emoji lookup file and publish to Sumo Logic

Usage:
   $ python  emoji_lookup  [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           emoji_lookup
    @version        1.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 1.00
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

### beginning ###
import json
import pprint
import os
import sys
import argparse
import http
import requests
sys.dont_write_bytecode = 1

MY_CFG = 'undefined'
PARSER = argparse.ArgumentParser(description="""
query_folders is a Sumo Logic cli cmdlet retrieving information about folders
""")

PARSER.add_argument("-a", metavar='<secret>', dest='MY_SECRET', \
                    help="set api (format: <key>:<secret>) ")
PARSER.add_argument("-k", metavar='<client>', dest='MY_CLIENT', \
                    help="set key (format: <site>_<orgid>) ")
PARSER.add_argument("-e", metavar='<endpoint>', dest='MY_ENDPOINT', \
                    help="set endpoint (format: <endpoint>) ")
PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="Increase verbosity")
PARSER.add_argument("-l", metavar='<lookupfile>', dest='MY_LOOKUP', \
                    help="set path for lookup file")
PARSER.add_argument("-j", metavar='<lookupcfg>', dest='MY_JSON', \
                    help="set path for lookup config JSON file")

ARGS = PARSER.parse_args()

if ARGS.MY_SECRET:
    (MY_APINAME, MY_APISECRET) = ARGS.MY_SECRET.split(':')
    os.environ['SUMO_UID'] = MY_APINAME
    os.environ['SUMO_KEY'] = MY_APISECRET

if ARGS.MY_CLIENT:
    (MY_DEPLOYMENT, MY_ORGID) = ARGS.MY_CLIENT.split('_')
    os.environ['SUMO_LOC'] = MY_DEPLOYMENT
    os.environ['SUMO_ORG'] = MY_ORGID
    os.environ['SUMO_TAG'] = ARGS.MY_CLIENT

if ARGS.MY_ENDPOINT:
    os.environ['SUMO_END'] = ARGS.MY_ENDPOINT
else:
    os.environ['SUMO_END'] = os.environ['SUMO_LOC']

if ARGS.MY_LOOKUP:
    os.environ['SUMO_CSV'] = ARGS.MY_LOOKUP
else:
    os.environ['SUMO_CSV'] = os.environ['SUMO_CSV']

if ARGS.MY_JSON:
    os.environ['SUMO_CFG'] = ARGS.MY_JSON
else:
    os.environ['SUMO_CFG'] = os.environ['SUMO_CFG']

try:

    SUMO_UID = os.environ['SUMO_UID']
    SUMO_KEY = os.environ['SUMO_KEY']
    SUMO_LOC = os.environ['SUMO_LOC']
    SUMO_ORG = os.environ['SUMO_ORG']
    SUMO_END = os.environ['SUMO_END']
    SUMO_CSV = os.environ['SUMO_CSV']
    SUMO_CFG = os.environ['SUMO_CFG']

except KeyError as myerror:

    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

PP = pprint.PrettyPrinter(indent=4)

### beginning ###

def main():
    """
    Setup the Sumo API connection, using the required tuple of region, id, and key.
    Once done, then issue the command required
    """
    source = SumoApiClient(SUMO_UID, SUMO_KEY, SUMO_END)
    run_sumo_cmdlet(source)

def run_sumo_cmdlet(source):
    """
    This will collect the information on object for sumologic and then collect that into a list.
    the output of the action will provide a tuple of the orgid, objecttype, and id
    """
    target_object = "myfolders"
    target_dict = dict()
    target_dict["orgid"] = SUMO_ORG
    target_dict[target_object] = dict()

    src_items = source.get_personal_folder()
    target_dict[target_object]['id'] = dict()
    target_dict[target_object]['id'].update({'parent' : SUMO_ORG})
    target_dict[target_object]['id'].update({'dump' : src_items})
    parent_id = target_dict['myfolders']['id']['dump']['id']

    createdir = 'yes'
    createlookup = 'yes'

    for folder in target_dict['myfolders']['id']['dump']['children']:
        if folder['name'] == 'lookupfiles':
            createdir = 'no'
            lookupdirname = folder['name']
            lookupdirid = folder['id']
            folderitems = source.get_folder(lookupdirid)
            for content in folderitems['children']:
                if content['name'] == 'emojilookup':
                    createlookup = 'no'
                    lookupfileid = content['id']
                    lookupfilename = content['name']

    if createdir == 'yes':
        result = source.create_folder('lookupfiles', parent_id)
        lookupdirname = result['name']
        lookupdirid = result['id']

    if ARGS.verbose > 3:
        print('LookupFolder: {} - {}'.format(lookupdirid, lookupdirname))

    if createlookup == 'yes':
        result = source.create_lookup('emojilookup', lookupdirid)
        lookupfileid = result['id']
        lookupfilename = result['name']

    if ARGS.verbose > 3:
        print('LookupFile: {} - {}'.format(lookupfileid, lookupfilename))

    if createlookup != 'yes':
        result = source.truncate_lookup(lookupfileid)
        if ARGS.verbose > 3:
            print('Truncating: {} - {}'.format(result['id'], lookupfileid))

    source.session.headers = None
    result = source.populate_lookup(lookupfileid, SUMO_CSV)
    if ARGS.verbose > 3:
        print('Populating: {} - {}'.format(result['id'], SUMO_CSV))

class SumoApiClient():
    """
    This is defined SumoLogic API Client
    The class includes the HTTP methods, cmdlets, and init methods
    """

    def __init__(self, access_id, access_key, region, cookieFile='cookies.txt'):
        """
        Initializes the Sumo Logic object
        """
        self.session = requests.Session()
        self.session.auth = (access_id, access_key)
        self.session.headers = {'content-type': 'application/json', \
            'accept': 'application/json'}
        self.apipoint = 'https://api.' + region + '.sumologic.com/api'
        cookiejar = http.cookiejar.FileCookieJar(cookieFile)
        self.session.cookies = cookiejar

    def delete(self, method, params=None, headers=None, data=None):
        """
        Defines a Sumo Logic Delete operation
        """
        response = self.session.delete(self.apipoint + method, \
            params=params, headers=headers, data=data)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def get(self, method, params=None, headers=None):
        """
        Defines a Sumo Logic Get operation
        """
        response = self.session.get(self.apipoint + method, \
            params=params, headers=headers)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def upload(self, method, headers=None, files=None):
        """
        Defines a Sumo Logic Post operation
        """
        response = self.session.post(self.apipoint + method, \
            headers=headers, files=files)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def post(self, method, data, headers=None, params=None):
        """
        Defines a Sumo Logic Post operation
        """
        response = self.session.post(self.apipoint + method, \
            data=json.dumps(data), headers=headers, params=params)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def put(self, method, data, headers=None, params=None):
        """
        Defines a Sumo Logic Put operation
        """
        response = self.session.put(self.apipoint + method, \
            data=json.dumps(data), headers=headers, params=params)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

### class ###
### methods ###

    def create_folder(self, folder_name, parent_id, adminmode=False):
        """
        creates a named folder
        """
        headers = {'isAdminMode': str(adminmode)}
        jsonpayload = {
            'name': folder_name,
            'parentId': str(parent_id)
        }

        url = '/v2/content/folders'
        body = self.post(url, jsonpayload, headers=headers).text
        results = json.loads(body)
        return results

    def create_lookup(self, _lookup_name, parent_id, adminmode=False):
        """
        creates a lookup file stub
        """
        headers = {'isAdminMode': str(adminmode)}

        with open (SUMO_CFG, "rb") as jsonobject:
            jsonpayload = json.load(jsonobject)
            jsonpayload['parentFolderId'] = parent_id

        url = '/v1/lookupTables'
        body = self.post(url, jsonpayload, headers=headers).text
        results = json.loads(body)
        return results

    def truncate_lookup(self, lookup_id):
        """
        truncates a lookup file
        """
        url = '/v1/lookupTables/' + str(lookup_id) + '/truncate'
        body = self.post(url, lookup_id).text
        results = json.loads(body)
        return results

    def populate_lookup(self, parent_id, csvfile):
        """
        populates a lookup file stub
        """

        with open(csvfile, "rb") as fileobject:
            csvpayload = fileobject.read()

        files = { 'file' : ( csvfile, csvpayload ) }

        url = '/v1/lookupTables/' + parent_id + '/upload'
        body = self.upload(url, files=files).text
        results = json.loads(body)
        return results

    def get_folder(self, folder_id, adminmode=False):
        """
        queries folders
        """
        headers = {'isAdminMode': str(adminmode).lower()}
        url = '/v2/content/folders/' + str(folder_id)
        body = self.get(url, headers=headers).text
        results = json.loads(body)
        return results

    def get_personal_folder(self):
        """
        get personal base folder
        """
        url = '/v2/content/folders/personal'
        body = self.get(url).text
        results = json.loads(body)
        return results

### methods ###

if __name__ == '__main__':
    main()
