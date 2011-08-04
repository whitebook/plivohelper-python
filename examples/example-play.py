#!/usr/bin/env python
import plivohelper
import sys


try:
    calluuid = sys.argv[1]
    sounds = sys.argv[2]
except IndexError:
    print "Need CallUUID Sounds args"
    sys.exit(1)

try:
    legs = sys.argv[3]
except IndexError:
    legs = ""

# URL of the Plivo REST Service
REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# Create a REST object
plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

call_params = {'CallUUID':calluuid, 'Sounds':sounds, 'Legs':legs}

try:
    print plivo.play(call_params)
except Exception, e:
    print e
