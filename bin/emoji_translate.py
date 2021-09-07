#!/usr/bin/env python3
"""
Converts an emoji into unicode string for display
"""

import sys
ename=sys.argv[1]
ecode=sys.argv[2]

LEAD = '\\' + 'u' + ecode

if len(ecode) != 4:
    offset = (len(bin(int(ecode,16))) - 10 )
    LEAD = str(hex(int(str((bin(int(ecode,16)))[2:offset]),2) + 55232))
    LEAD = LEAD.replace('0x', "\\u")
    TAIL = str(hex( (int(ecode, 16) & 1023 ) + 56320 ))
    TAIL = TAIL.replace('0x', "\\u")
    conversion = LEAD + TAIL
else:
    conversion = LEAD

print('NAME: {}\t CODE: {}\t CONVERSION: {}'.format(ename, ecode, conversion))
