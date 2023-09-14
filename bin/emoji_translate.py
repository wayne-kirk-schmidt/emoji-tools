#!/usr/bin/env python3

# pylint: disable=C0209

"""
Converts an emoji into unicode string for display
"""

import sys

ENAME=sys.argv[1]

ECODELIST=sys.argv[2:]

CONVERTLIST = []

for ecode in ECODELIST:

    ecode = ecode.replace('U+','')

    if len(ecode) != 4:
        offset = (len(bin(int(ecode,16))) - 10 )
        LEAD = str(hex(int(str((bin(int(ecode,16)))[2:offset]),2) + 55232))
        LEAD = LEAD.replace('0x', "\\u")
        TAIL = str(hex( (int(ecode, 16) & 1023 ) + 56320 ))
        TAIL = TAIL.replace('0x', "\\u")
        CONVERSION = LEAD + TAIL
    else:
        LEAD = '\\' + 'u' + ecode
        CONVERSION = LEAD

    CONVERTLIST.append(CONVERSION)

SEPARATOR = ''
CONVERTED = SEPARATOR.join(CONVERTLIST)
print('NAME: {}\t CODELIST: {}'.format(ENAME, ECODELIST))
print('NAME: {}\t CONVERTED: {}'.format(ENAME, CONVERTED))
