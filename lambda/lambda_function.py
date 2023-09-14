# pylint: disable=C0209
"""
AWS Lambda function for downloading, processing, and uploading emojifiles into Sumo Logic
"""

import json
import os
import sys
import configparser
import http
import urllib.parse
import string
import requests
import bs4
sys.dont_write_bytecode = 1

VERBOSE = 0
CFGFILE = './lambda_function.cfg'

CONFIG = configparser.ConfigParser()
CONFIG.optionxform = str

CONFIG.read(CFGFILE)

if CONFIG.has_option("Default", "SUMO_UID"):
    SUMO_UID = CONFIG.get("Default", "SUMO_UID")
    os.environ['SUMO_UID'] = SUMO_UID

if CONFIG.has_option("Default", "SUMO_KEY"):
    SUMO_KEY = CONFIG.get("Default", "SUMO_KEY")
    os.environ['SUMO_KEY'] = SUMO_KEY

if CONFIG.has_option("Default", "SUMO_ORG"):
    SUMO_ORG = CONFIG.get("Default", "SUMO_ORG")
    os.environ['SUMO_ORG'] = SUMO_ORG

if CONFIG.has_option("Default", "SUMO_END"):
    SUMO_END = CONFIG.get("Default", "SUMO_END")
    os.environ['SUMO_END'] = SUMO_END

if CONFIG.has_option("Default", "CSV_FILE"):
    CSV_FILE = CONFIG.get("Default", "CSV_FILE")
    os.environ['CSV_FILE'] = CSV_FILE

if CONFIG.has_option("Default", "CSV_JSON"):
    CSV_JSON = CONFIG.get("Default", "CSV_JSON")
    os.environ['CSV_JSON'] = CSV_JSON

TARGETURL = 'https://unicode.org/emoji/charts/full-emoji-list.html'
HTMLFILE = os.path.join( '/tmp', os.path.basename(urllib.parse.urlsplit(TARGETURL).path) )
CSV_LIST = []

try:

    SUMO_UID = os.environ['SUMO_UID']
    SUMO_KEY = os.environ['SUMO_KEY']
    SUMO_ORG = os.environ['SUMO_ORG']
    SUMO_END = os.environ['SUMO_END']
    CSV_FILE = os.environ['CSV_FILE']
    CSV_JSON = os.environ['CSV_JSON']

except KeyError as myerror:

    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

### def main():
def lambda_handler(_event,_context):
    """
    Lambda handler driver. An event and context can also be used to process results.
    """

    source = SumoApiClient(SUMO_UID, SUMO_KEY, SUMO_END)
    download_html_file(TARGETURL,HTMLFILE)
    process_html_file(HTMLFILE)
    run_sumo_cmdlet(source)

def download_html_file(emojiurl, emojifile):
    """
    Download the file from the unicode.org site. This should be all of the registered emojis
    """
    url = requests.get(emojiurl, timeout=15 )
    htmltext = url.text
    with open(emojifile, 'w', encoding="utf-8" ) as outputfile:
        outputfile.write(htmltext)

def expandcode(codestring: str):
    """
    Process the target name and code string item
    """
    return chr(int(codestring.lstrip("U+").zfill(8), 16))

def process_emoji(ename, codelist):
    """
    Process the target name and code list
    """
    convertlist = []
    for codeitem in codelist.split():
        ### converted = convertcode(codeitem)
        converted = expandcode(codeitem)
        convertlist.append(converted)

    separator = ''
    codestring = separator.join(convertlist)

    CSV_LIST.append( '\"' + ename + '\"' + ',' + '\"' + codestring + '\"' )

def convertcode(ecode):
    """
    This is the core of the algorithm for converting the file into appropriate strings for display
    """

    ecode = ecode.replace('U+','')
    lead = '\\\\' + 'u' + ecode

    if len(ecode) != 4:
        offset = (len(bin(int(ecode,16))) - 10 )
        lead = str(hex(int(str((bin(int(ecode,16)))[2:offset]),2) + 55232))
        lead = lead.replace('0x', "\\\\u")
        tail = str(hex( (int(ecode, 16) & 1023 ) + 56320 ))
        tail = tail.replace('0x', "\\\\u")
        conversion = lead + tail
    else:
        conversion = lead

    return conversion

def process_html_file(emojifile):
    """
    Parse the html file and extract the name and code point
    """
    CSV_LIST.append( '\"emojiname\"' + ',' + '\"emojicode\"' )
    with open(emojifile, 'r', encoding="utf-8") as emoji_html:
        soup = bs4.BeautifulSoup(emoji_html, "html.parser")
        for row in soup.find_all('tr'):
            name = row.find('td', attrs={'class': 'name'})
            if name is not None:
                emojiname = name.text
                emojiname = emojiname.translate(emojiname.maketrans('', '', string.punctuation))
                emojiname = emojiname.replace(' ', '_')
                emojiname = emojiname.replace('__', '_')
                emojiname = emojiname.lower()

            code = row.find('td', attrs={'class': 'code'})
            if name is not None:
                emojicode = code.text
            if name is not None:
                process_emoji(emojiname, emojicode)

    with open(CSV_FILE, 'w', encoding="utf-8") as outfile:
        outfile.write("\n".join(CSV_LIST))

def run_sumo_cmdlet(source):
    """
    This will build within Sumo Logic the necessary files and folders
    """

    target_object = "myfolders"
    target_dict = {}
    target_dict["orgid"] = SUMO_ORG
    target_dict[target_object] = {}

    src_items = source.get_personal_folder()
    target_dict[target_object]['id'] = {}
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

    if VERBOSE > 3:
        print('LookupFolder: {} - {}'.format(lookupdirid, lookupdirname))

    if createlookup == 'yes':
        result = source.create_lookup('emojilookup', lookupdirid)
        lookupfileid = result['id']
        lookupfilename = result['name']

    if VERBOSE > 3:
        print('LookupFile: {} - {}'.format(lookupfileid, lookupfilename))

    if createlookup != 'yes':
        result = source.truncate_lookup(lookupfileid)
        if VERBOSE > 3:
            print('Truncating: {} - {}'.format(result['id'], lookupfileid))

    source.session.headers = None
    result = source.populate_lookup(lookupfileid, CSV_FILE)
    if VERBOSE > 3:
        print('Populating: {} - {}'.format(result['id'], CSV_FILE))

class SumoApiClient():
    """
    This is defined SumoLogic API Client
    The class includes the HTTP methods, cmdlets, and init methods
    """

    def __init__(self, access_id, access_key, region, cookie_file='cookies.txt'):
        """
        Initializes the Sumo Logic object
        """
        self.session = requests.Session()
        self.session.auth = (access_id, access_key)
        self.session.headers = {'content-type': 'application/json', \
            'accept': 'application/json'}
        self.apipoint = 'https://api.' + region + '.sumologic.com/api'
        cookiejar = http.cookiejar.FileCookieJar(cookie_file)
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

        with open (CSV_JSON, 'r', encoding="utf-8" ) as jsonobject:
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

        with open(csvfile, 'r', encoding="utf-8" ) as fileobject:
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

### if __name__ == '__main__':
###     main()
