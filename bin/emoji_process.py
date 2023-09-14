#!/usr/bin/env python3

# pylint: disable=C0209

"""
Downloads and processes the emoji list
"""

import os
import urllib.parse
import string
import requests
import bs4


TARGETURL = 'https://unicode.org/emoji/charts/full-emoji-list.html'

HTMLFILE = os.path.basename(urllib.parse.urlsplit(TARGETURL).path)

TARGETFILE = os.path.join( '/var/tmp', HTMLFILE )

def expandcode(codestring: str):
    """
    Process the target name and code string item
    """
    return chr(int(codestring.lstrip("U+").zfill(8), 16))

def process_emoji(ename, codelist):
    """
    Process the target name as well as the code list
    """
    convertlist = []
    for codeitem in codelist.split():
        ### converted = convertcode(codeitem)
        converted = expandcode(codeitem)
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
    print('\"{}\",\"{}\"'.format("emojiname", "emojicode"))
    with open (emojifile, 'r', encoding="utf-8" ) as emoji_html:
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

    url = requests.get(TARGETURL, timeout=15 )
    htmltext = url.text

    with open (TARGETFILE, 'w', encoding="utf-8" ) as outputfile:
        outputfile.write(htmltext)

    process_html_file(TARGETFILE)

if __name__ == '__main__':
    main()
