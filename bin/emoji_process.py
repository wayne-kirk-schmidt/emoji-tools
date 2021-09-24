#!/usr/bin/env python3

"""
Downloads and processes the emoji list
"""

import os
import sys
import urllib.parse
import string
import requests
import bs4


### targeturl = sys.argv[1]

targeturl = 'https://unicode.org/emoji/charts/full-emoji-list.html'

htmlfile = os.path.basename(urllib.parse.urlsplit(targeturl).path)

targetfile = os.path.join( '/var/tmp', htmlfile )

def download_html_file(emojiurl, emojifile):
    """
    Download the html file
    """
    url = requests.get(emojiurl)
    htmltext = url.text

    with open(emojifile, 'w') as outputfile:
        outputfile.write(htmltext)

def process_emoji(ename, codelist):
    """
    Process the target name and code list
    """
    convertlist = list()
    for codeitem in codelist.split():
        converted = convertcode(codeitem)
        convertlist.append(converted)

    separator = ''
    codestring = separator.join(convertlist)

    print('\"{}\",\"{}\"'.format(ename, codestring))

def convertcode(ecode):
    """
    Process codelist
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
    print('{},{}'.format("emojiname", "emojicode"))
    with open(emojifile) as emoji_html:
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

def main():
    """
    Driver for downloading, processing, and outputing emoticons
    """
    download_html_file(targeturl,targetfile)
    process_html_file(targetfile)

if __name__ == '__main__':
    main()
