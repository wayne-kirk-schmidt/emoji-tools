#!/usr/bin/env python3
"""
Converts an emoji into unicode string for display
"""

import sys

ename=sys.argv[1]

ecodelist=sys.argv[2:]

convertlist = list()

for ecode in ecodelist:

    ecode = ecode.replace('U+','')

    if len(ecode) != 4:
        offset = (len(bin(int(ecode,16))) - 10 )
        LEAD = str(hex(int(str((bin(int(ecode,16)))[2:offset]),2) + 55232))
        LEAD = LEAD.replace('0x', "\\u")
        TAIL = str(hex( (int(ecode, 16) & 1023 ) + 56320 ))
        TAIL = TAIL.replace('0x', "\\u")
        conversion = LEAD + TAIL
    else:
        LEAD = '\\' + 'u' + ecode
        conversion = LEAD

    convertlist.append(conversion)

SEPARATOR = ''
CONVERTED = SEPARATOR.join(convertlist)
print('NAME: {}\t CODELIST: {}'.format(ename, ecodelist))
print('NAME: {}\t CONVERTED: {}'.format(ename, CONVERTED))
