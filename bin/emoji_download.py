#!/usr/bin/env python3

# pylint: disable=C0209

"""
Exaplanation: emoji_download. Download the reference emoji file.

Usage:
   $ python  emoji_download  [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           emoji_download
    @version        1.00
    @author-name    Wayne Kirk Schmidt
    @author-email   wayne.kirk.schmidt@changeis.co.jp
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 1.00
__author__ = "Wayne Kirk Schmidt (wayne.kirk.schmidt@changeis.co.jp)"

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
