#!/usr/bin/env python3

"""
Downloads the emoji list
"""
### https://unicode.org/emoji/charts/full-emoji-list.html

import os
import sys
import urllib.parse
import requests

targeturl = sys.argv[1]
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

def main():
    """
    Driver for downloading, processing, and outputing emoticons
    """
    download_html_file(targeturl,targetfile)

if __name__ == '__main__':
    main()
