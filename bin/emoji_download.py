#!/usr/bin/env python3

# pylint: disable=C0209

"""
Downloads the emoji list
"""
### https://unicode.org/emoji/charts/full-emoji-list.html

import os
import urllib.parse
import requests

TARGETURL = 'https://unicode.org/emoji/charts/full-emoji-list.html'

HTMLFILE = os.path.basename(urllib.parse.urlsplit(TARGETURL).path)

TARGETFILE = os.path.join( '/var/tmp', HTMLFILE )

def main():
    """
    Driver for downloading, processing, and outputing emoticons
    """
    url = requests.get(TARGETURL, timeout=15 )
    htmltext = url.text

    with open (TARGETFILE, 'w', encoding="utf-8" ) as outputfile:
        outputfile.write(htmltext)


if __name__ == '__main__':
    main()
